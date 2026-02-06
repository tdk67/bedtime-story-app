import asyncio
import re
from openai import OpenAI
import google.generativeai as genai
from PIL import Image
from .config import GenerationConfig, config as gen_config

# --- Text Generation ---
def parse_story_and_choices(response_text: str):
    """
    Parses the AI's response to extract the narrative and choices,
    handling both [bracketed] and numbered list formats.
    """
    # First, try to find the preferred bracketed format
    choices = re.findall(r'\[(.*?)\]', response_text)
    narrative_part = re.split(r'\[', response_text)[0].strip()

    # If no bracketed choices are found, look for a numbered list
    if not choices:
        # This regex finds lines starting with "1.", "2.", "1)", etc.
        numbered_choices = re.findall(r'^\s*\d+[\.\)]\s*(.*)', response_text, re.MULTILINE)
        if numbered_choices:
            choices = numbered_choices
            # Find the start of the first choice to accurately get the narrative part
            first_choice_text = choices[0]
            # We need to find the original line to split correctly
            for line in response_text.splitlines():
                if first_choice_text in line:
                    narrative_part = response_text.split(line, 1)[0].strip()
                    break

    # Clean up any leading/trailing whitespace from choices
    cleaned_choices = [choice.strip() for choice in choices]
    return narrative_part, cleaned_choices

def get_story_prompt(app_config: dict) -> str:
    """Builds the system prompt from the configuration."""
    child_info = app_config.get("child_info", {})
    personalization = app_config.get("personalization", {})
    details = ", ".join(
        f"{key.replace('_', ' ')} is {value}" for key, value in personalization.items() if value
    )
    return gen_config.story_prompt.format(
        age=child_info.get('age', 5),
        name=child_info.get('name', 'Friend'),
        details=details
    )

async def generate_story_text(client: OpenAI, history: list):
    """Generates the next story segment using the configured text model."""
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=gen_config.providers.openai.text_model,
        messages=history,
        temperature=0.8
    )
    return response.choices[0].message.content

# --- Audio Generation ---

async def generate_audio_bytes(client: OpenAI, text: str, voice: str) -> bytes:
    """Generates audio from text using the configured TTS model."""
    response = await asyncio.to_thread(
        client.audio.speech.create,
        model=gen_config.providers.openai.tts_model,
        voice=voice,
        input=text
    )
    return response.content

# --- Image Generation ---

async def generate_image_bytes(prompt: str, reference_image: Image, high_quality: bool = False) -> bytes:
    """Generates an image from a prompt using the configured image model."""
    model = genai.GenerativeModel(gen_config.providers.google.image_model)

    full_prompt = f"{prompt}. The main character should look like the person in the provided image especially the face, the eyes, the nose, the chin should be recognizable."
    if high_quality:
        full_prompt += " A beautiful, high-quality, square (1:1) storybook illustration in a whimsical, gentle art style."
    else:
        full_prompt += " A small, square (1:1), simple, clear, cute icon on a plain white background."

    response = await asyncio.to_thread(model.generate_content, [full_prompt, reference_image])

    if response.candidates:
        for candidate in response.candidates:
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if part.inline_data:
                        return part.inline_data.data

    raise ValueError("No image data found in the API response.")