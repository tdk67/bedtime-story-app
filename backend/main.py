import os
import uuid
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv("../.env")

# --- Configuration & Initialization ---
app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create a directory for static files (audio) if it doesn't exist
STATIC_DIR = Path("static")
AUDIO_DIR = STATIC_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Mount the static directory to serve files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- Pydantic Models for API data structure ---
class StoryChoice(BaseModel):
    text: str
    audio_url: str

class StorySegment(BaseModel):
    story_text: str
    story_audio_url: str
    choices: list[StoryChoice]
    conversation_history: list[dict]

class StoryRequest(BaseModel):
    conversation_history: list[dict]
    choice: str | None = None
    config: dict

# --- Helper Functions ---
def get_story_prompt(config: dict):
    # This is the same master prompt from the previous version
    child_info = config.get("child_info", {})
    personalization = config.get("personalization", {})
    personalization_details = ", ".join(
        f"{key.replace('_', ' ')} is {value}"
        for key, value in personalization.items()
        if value is not None
    )
    # The prompt remains the same...
    return f"""
    You are a world-class bedtime storyteller for a {child_info.get('age', 6)}-year-old child named {child_info.get('name', 'Friend')}.
    Your primary goal is to create a gentle, interactive, and personalized story that always ends happily and teaches a positive lesson.
    **STORY RULES:**
    1.  **Main Character:** The main character is ALWAYS {child_info['name']}.
    2.  **Personalization:** Seamlessly weave these personal details into the story: {personalization_details}.
    3.  **Tone:** Keep the tone calm, positive, and reassuring. Absolutely NO scary, violent, or sad themes.
    4.  **Structure:** Narrate in short segments (3-4 sentences). At the end of EACH segment, you MUST ask a question with 2 or 3 clear choices.
    5.  **Choice Format:** Present the choices clearly using bracketed format, like this: [Choice 1] or [Choice 2].
    6.  **Pacing:** The entire story must conclude in 5 to 8 steps.
    7.  **Moral:** The story must have a clear, simple, and positive moral lesson.
    8.  **Happy Ending:** The story MUST have a happy and satisfying conclusion.
    **INITIAL TASK:**
    Do not start the story yet. Your first task is to ask a single, imaginative question with three choices to help {child_info['name']} choose an adventure.
    """

def generate_tts(text: str, voice: str) -> str:
    """Generates audio from text and returns the URL path."""
    try:
        filename = f"{uuid.uuid4()}.mp3"
        filepath = AUDIO_DIR / filename
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        response.stream_to_file(filepath)
        # Return the web-accessible path
        return f"/static/audio/{filename}"
    except Exception:
        # Return an empty string or error path if TTS fails
        return ""

def parse_story_and_choices(response_text: str):
    """Parses the LLM response into story text and a list of choices."""
    choices_text = re.findall(r'\[(.*?)\]', response_text)
    story_part = re.split(r'\[', response_text)[0].strip()
    return story_part, choices_text

# --- API Endpoints ---
@app.post("/start_story", response_model=StorySegment)
async def start_story(request: StoryRequest):
    """Generates the first part of the story."""
    system_prompt = get_story_prompt(request.config)
    
    history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Let's begin the story."}
    ]

    response = client.chat.completions.create(
        model="gpt-4o", messages=history, temperature=0.8
    )
    llm_response_text = response.choices[0].message.content
    history.append({"role": "assistant", "content": llm_response_text})

    story_text, choices_list = parse_story_and_choices(llm_response_text)
    voice = request.config.get("voice", "alloy")

    # Generate audio for all parts
    story_audio_url = generate_tts(story_text, voice)
    choices_with_audio = [
        {"text": choice, "audio_url": generate_tts(choice, voice)}
        for choice in choices_list
    ]

    return {
        "story_text": story_text,
        "story_audio_url": story_audio_url,
        "choices": choices_with_audio,
        "conversation_history": history
    }

@app.post("/next_step", response_model=StorySegment)
async def next_step(request: StoryRequest):
    """Generates the next segment of the story based on user's choice."""
    history = request.conversation_history
    history.append({"role": "user", "content": request.choice})

    response = client.chat.completions.create(
        model="gpt-4o", messages=history, temperature=0.8
    )
    llm_response_text = response.choices[0].message.content
    history.append({"role": "assistant", "content": llm_response_text})
    
    story_text, choices_list = parse_story_and_choices(llm_response_text)
    voice = request.config.get("voice", "alloy")

    story_audio_url = generate_tts(story_text, voice)
    choices_with_audio = [
        {"text": choice, "audio_url": generate_tts(choice, voice)}
        for choice in choices_list
    ]
    
    # Check for the end of the story
    if not choices_list or "the end" in story_text.lower():
        choices_with_audio = []

    return {
        "story_text": story_text,
        "story_audio_url": story_audio_url,
        "choices": choices_with_audio,
        "conversation_history": history
    }