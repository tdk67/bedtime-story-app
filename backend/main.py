import os
import uuid
import base64
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import re
import google.generativeai as genai
from PIL import Image
from io import BytesIO

# Load environment variables
load_dotenv("../.env")

# --- Configuration & Initialization ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app.state.jobs = {}

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

# --- Helper Functions ---
def get_story_prompt(config: dict):
    child_info = config.get("child_info", {})
    personalization = config.get("personalization", {})
    personalization_details = ", ".join(
        f"{key.replace('_', ' ')} is {value}" for key, value in personalization.items() if value
    )
    return f"""
    You are a world-class bedtime storyteller for a {child_info.get('age', 6)}-year-old child named {child_info.get('name', 'Friend')}.
    Your primary goal is to create a gentle, interactive, and personalized story.

    **STORY RULES:**
    1.  **Main Character:** The main character is ALWAYS {child_info['name']}.
    2.  **Personalization:** Seamlessly weave these personal details into the story: {personalization_details}.
    3.  **Tone:** Keep the tone calm, positive, and reassuring. Absolutely NO scary, violent, or sad themes.
    4.  **Structure:** Your task is to generate ONLY ONE segment of the story at a time. A segment consists of 3-4 sentences of narration, followed by a question with 2 or 3 clear choices.
    5.  **Choice Format:** Present the choices clearly using bracketed format, like this: [Choice 1] or [Choice 2].
    6.  **Pacing:** Guide the story towards a conclusion over the course of 5 to 8 total segments. Ensure the story does not end prematurely.
    7.  **Moral:** The story must have a clear, simple, and positive moral lesson.
    8.  **Happy Ending:** The story MUST have a happy and satisfying conclusion.

    **INITIAL TASK:**
    For the very first turn, do not start the story. Your first task is to ask a single, imaginative question with three choices to help {child_info['name']} choose an adventure.
    """

def generate_tts_bytes(text: str, voice: str) -> bytes | None:
    try:
        response = client.audio.speech.create(model="tts-1", voice=voice, input=text)
        return response.content
    except Exception as e:
        print(f"Error generating TTS: {e}")
        return None

def generate_image_bytes(prompt: str, reference_image: Image, high_quality: bool = False) -> bytes | None:
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
        
        full_prompt = f"{prompt}. The main character should look like the person in the provided image."
        if high_quality:
            # --- FIX: Request a 1:1 aspect ratio for the main illustration ---
            full_prompt += " Generate a beautiful, high-quality, square (1:1 aspect ratio) storybook illustration in a whimsical and gentle art style."
        else:
            full_prompt += " Generate a small, square (1:1 aspect ratio), simple, clear, and cute icon-style image on a plain white background, showing only the key object/concept of the choice."
        
        response = model.generate_content([full_prompt, reference_image])
        
        if response.candidates:
            first_candidate = response.candidates[0]
            if first_candidate.content and first_candidate.content.parts:
                for part in first_candidate.content.parts:
                    if part.inline_data:
                        return part.inline_data.data
        return None

    except Exception as e:
        print(f"Error generating Image: {e}")
        return None


def parse_story_and_choices(response_text: str):
    choices_text = re.findall(r'\[(.*?)\]', response_text)
    story_part = re.split(r'\[', response_text)[0].strip()
    return story_part, choices_text

# --- Background Processing & Endpoints ---
def process_story_in_background(job_id: str, history: list, config: dict):
    try:
        app.state.jobs[job_id]['status'] = 'generating_text'
        response = client.chat.completions.create(model="gpt-4o", messages=history, temperature=0.8)
        llm_response_text = response.choices[0].message.content
        history.append({"role": "assistant", "content": llm_response_text})

        app.state.jobs[job_id]['status'] = 'generating_media'
        story_text, choices_list_text = parse_story_and_choices(llm_response_text)
        voice = config.get("voice", "alloy")

        text_for_narration = story_text
        if choices_list_text:
            text_for_narration += " " + " ".join(choices_list_text)

        narration_audio_bytes = generate_tts_bytes(text_for_narration, voice) or b""
        narration_audio_b64 = base64.b64encode(narration_audio_bytes).decode('utf-8')
        
        child_photo_path = os.path.join("../frontend", config['child_photo_path'])
        reference_image = Image.open(child_photo_path)
        
        main_illustration_bytes = generate_image_bytes(story_text, reference_image, high_quality=True) or b""
        main_illustration_b64 = base64.b64encode(main_illustration_bytes).decode('utf-8')

        choices_with_media = []
        for choice_text in choices_list_text:
            choice_audio_bytes = generate_tts_bytes(choice_text, voice) or b""
            choice_audio_b64 = base64.b64encode(choice_audio_bytes).decode('utf-8')
            
            choice_image_bytes = generate_image_bytes(choice_text, reference_image) or b""
            choice_image_b64 = base64.b64encode(choice_image_bytes).decode('utf-8')

            choices_with_media.append({
                "text": choice_text, 
                "audio_b64": choice_audio_b64, 
                "image_b64": choice_image_b64
            })

        result = {
            "story_text": story_text,
            "narration_audio_b64": narration_audio_b64,
            "main_illustration_b64": main_illustration_b64,
            "choices": choices_with_media,
            "conversation_history": history
        }
        app.state.jobs[job_id]['result'] = result
        app.state.jobs[job_id]['status'] = 'complete'

    except Exception as e:
        print(f"Error in background task: {e}")
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