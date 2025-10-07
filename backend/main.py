import os
import uuid
import base64
import re
import yaml
import asyncio
from io import BytesIO

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

# Import from our new refactored modules
from generation.config import config as gen_config
from generation.generators import (
    get_story_prompt, 
    generate_story_text, 
    generate_audio_bytes, 
    generate_image_bytes,
    parse_story_and_choices
)

# Load environment variables from the root .env file
load_dotenv("../.env")

# --- Initialization ---
app = FastAPI()

# Add CORS middleware to allow requests from the HTML frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# In-memory job storage
app.state.jobs = {}

# --- API Endpoints ---

@app.get("/config")
async def get_frontend_config():
    """
    Reads the frontend's config.yaml file and returns it as JSON.
    """
    try:
        with open("../frontend/config.yaml", 'r') as file:
            config_data = yaml.safe_load(file)
        return config_data
    except FileNotFoundError:
        return {"error": "frontend/config.yaml not found"}
    except Exception as e:
        return {"error": str(e)}

# --- Pydantic Models ---
class StoryChoice(BaseModel):
    text: str
    audio_b64: str
    image_b64: str

class StorySegment(BaseModel):
    story_text: str
    narration_audio_b64: str
    main_illustration_b64: str
    choices: list[StoryChoice]
    conversation_history: list[dict]

class GenerationRequest(BaseModel):
    conversation_history: list[dict] | None = None
    choice: str | None = None
    config: dict

class JobResponse(BaseModel):
    job_id: str

class StatusResponse(BaseModel):
    job_id: str
    status: str

# --- Background Processing ---
async def process_story_in_background(job_id: str, history: list, app_config: dict):
    try:
        app.state.jobs[job_id]['status'] = 'generating_text'
        llm_response_text = await generate_story_text(client, history)
        history.append({"role": "assistant", "content": llm_response_text})
        story_text, choices_list_text = parse_story_and_choices(llm_response_text)
        
        app.state.jobs[job_id]['status'] = 'generating_media'
        voice = app_config.get("voice", "alloy")
        child_photo_path = os.path.join("../frontend", app_config['child_photo_path'])
        reference_image = Image.open(child_photo_path)

        tasks = []
        narration_text = story_text + " " + " ".join(choices_list_text)
        tasks.append(generate_audio_bytes(client, narration_text, voice))
        tasks.append(generate_image_bytes(story_text, reference_image, high_quality=True))
        
        for choice_text in choices_list_text:
            tasks.append(generate_audio_bytes(client, choice_text, voice))
            tasks.append(generate_image_bytes(choice_text, reference_image))

        print(f"Starting {len(tasks)} media generation tasks in parallel for job {job_id}...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        print(f"All media generation tasks finished for job {job_id}.")
        
        def get_result_or_default(result, task_name, default_value):
            if isinstance(result, Exception):
                print(f"ERROR: Task '{task_name}' failed for job {job_id}: {result}")
                return default_value
            return result

        narration_audio_bytes = get_result_or_default(results[0], "Main Narration", b"")
        main_illustration_bytes = get_result_or_default(results[1], "Main Illustration", b"")

        choices_with_media = []
        choice_results = results[2:] 
        for i, choice_text in enumerate(choices_list_text):
            audio_result_index = i * 2
            image_result_index = i * 2 + 1
            choice_audio_bytes = get_result_or_default(choice_results[audio_result_index], f"Choice Audio '{choice_text}'", b"")
            choice_image_bytes = get_result_or_default(choice_results[image_result_index], f"Choice Image '{choice_text}'", b"")
            choices_with_media.append({
                "text": choice_text,
                "audio_b64": base64.b64encode(choice_audio_bytes).decode('utf-8'),
                "image_b64": base64.b64encode(choice_image_bytes).decode('utf-8')
            })

        final_result = {
            "story_text": story_text,
            "narration_audio_b64": base64.b64encode(narration_audio_bytes).decode('utf-8'),
            "main_illustration_b64": base64.b64encode(main_illustration_bytes).decode('utf-8'),
            "choices": choices_with_media,
            "conversation_history": history
        }
        app.state.jobs[job_id]['result'] = final_result
        app.state.jobs[job_id]['status'] = 'complete'

    except Exception as e:
        print(f"FATAL ERROR in background task for job {job_id}: {e}")
        app.state.jobs[job_id]['status'] = 'failed'

@app.post("/generate/start", response_model=JobResponse)
async def start_generation(request: GenerationRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    app.state.jobs[job_id] = {"status": "pending"}

    if request.conversation_history and request.choice:
        history = request.conversation_history
        history.append({"role": "user", "content": request.choice})
    else:
        system_prompt = get_story_prompt(request.config)
        history = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "Let's begin."}]

    background_tasks.add_task(process_story_in_background, job_id, history, request.config)
    return {"job_id": job_id}

@app.get("/generate/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    job = app.state.jobs.get(job_id, {})
    return {"job_id": job_id, "status": job.get("status", "not_found")}

@app.get("/generate/result/{job_id}")
async def get_result(job_id: str):
    job = app.state.jobs.get(job_id, {})
    return job.get("result", {})