import asyncio
import os
from dotenv import load_dotenv
from openai import OpenAI

from backend.generation.generators import generate_audio_bytes

async def main():
    print("--- Testing Audio Generation ---")
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        text = "Hello, this is a test of the text-to-speech system."
        voice = "onyx" #alloy, echo, fable, onyx, nova, shimmer
        
        print(f"Text: '{text}'")
        
        audio_data = await generate_audio_bytes(client, text, voice)
        
        output_path = "test_audio_output_"+voice+".mp3"
        with open(output_path, "wb") as f:
            f.write(audio_data)
            
        print(f"\n✅ SUCCESS: Audio saved to '{output_path}' in your project root.")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())