import os
import base64
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv("../.env")

# --- Configuration & Initialization ---
app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Pydantic Models ---
# The choice model now includes its own audio data again
class StoryChoice(BaseModel):
    text: str
    audio_b64: str

# The main response sends a combined narration audio AND choices with their own audio
class StorySegment(BaseModel):
    story_text: str
    narration_audio_b64: str
    choices: list[StoryChoice]
    conversation_history: list[dict]

class StartStoryRequest(BaseModel):
    config: dict

class NextStepRequest(BaseModel):
    conversation_history: list[dict]
    choice: str
    config: dict

# --- Helper Functions (generate_tts_bytes, parse_story_and_choices, get_story_prompt) remain the same ---
def generate_tts_bytes(text: str, voice: str) -> bytes | None:
    """Generates audio from text and returns it as bytes."""
    try:
        response = client.audio.speech.create(model="tts-1", voice=voice, input=text)
        return response.content
    except Exception as e:
        print(f"Error generating TTS: {e}")
        return None

def parse_story_and_choices(response_text: str):
    choices_text = re.findall(r'\[(.*?)\]', response_text)
    story_part = re.split(r'\[', response_text)[0].strip()
    return story_part, choices_text

def get_story_prompt(config: dict):
    child_info = config.get("child_info", {})
    personalization = config.get("personalization", {})
    personalization_details = ", ".join(
        f"{key.replace('_', ' ')} is {value}" for key, value in personalization.items() if value
    )
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

# --- API Endpoints ---
async def process_story_segment(history: list, config: dict) -> StorySegment:
    response = client.chat.completions.create(model="gpt-4o", messages=history, temperature=0.8)
    llm_response_text = response.choices[0].message.content
    history.append({"role": "assistant", "content": llm_response_text})

    story_text, choices_list_text = parse_story_and_choices(llm_response_text)
    voice = config.get("voice", "alloy")

    # --- NEW HYBRID AUDIO LOGIC ---

    # 1. Generate the combined audio for seamless narration
    text_for_narration = story_text
    if choices_list_text:
        choices_narration = ". ".join(choices_list_text)
        text_for_narration += f" {choices_narration}"
    
    narration_audio_bytes = generate_tts_bytes(text_for_narration, voice) or b""
    narration_audio_b64 = base64.b64encode(narration_audio_bytes).decode('utf-8')

    # 2. Generate individual audio for each choice for the replay buttons
    choices_with_audio = []
    for choice_text in choices_list_text:
        choice_audio_bytes = generate_tts_bytes(choice_text, voice) or b""
        choice_audio_b64 = base64.b64encode(choice_audio_bytes).decode('utf-8')
        choices_with_audio.append({"text": choice_text, "audio_b64": choice_audio_b64})

    if not choices_list_text or "the end" in story_text.lower():
        choices_with_audio = []

    return StorySegment(
        story_text=story_text,
        narration_audio_b64=narration_audio_b64,
        choices=choices_with_audio,
        conversation_history=history
    )

@app.post("/start_story", response_model=StorySegment)
async def start_story(request: StartStoryRequest):
    system_prompt = get_story_prompt(request.config)
    history = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "Let's begin."}]
    return await process_story_segment(history, request.config)

@app.post("/next_step", response_model=StorySegment)
async def next_step(request: NextStepRequest):
    history = request.conversation_history
    history.append({"role": "user", "content": request.choice})
    return await process_story_segment(history, request.config)