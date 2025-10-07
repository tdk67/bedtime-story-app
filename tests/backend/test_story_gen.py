import asyncio
import os
import re
from dotenv import load_dotenv
from openai import OpenAI

from backend.generation.generators import generate_story_text, get_story_prompt

def parse_story_and_choices(response_text: str):
    choices_text = re.findall(r'\[(.*?)\]', response_text)
    story_part = re.split(r'\[', response_text)[0].strip()
    return story_part, choices_text

async def main():
    print("--- Testing Text Generation ---")
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Mock the config that comes from the frontend
        mock_app_config = {
            "child_info": {"name": "Alex", "age": 6},
            "personalization": {"favourite_animal": "lion"}
        }
        
        system_prompt = get_story_prompt(mock_app_config)
        history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Let's begin."}
        ]
        
        print("Generating initial story prompt...")
        response =  await generate_story_text(client, history)
        story_text, choices = parse_story_and_choices(response)        
        
        print("\n✅ SUCCESS: Generated story segment:")
        print("-" * 30)
        print(story_text)
        print("choices="+str(choices))
        print("-" * 30)
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())