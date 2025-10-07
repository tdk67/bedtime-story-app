import asyncio
import os
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

# Absolute import from the 'backend' package
from backend.generation.generators import generate_image_bytes

async def main():
    print("--- Testing Image Generation ---")
    
    try:
        ref_image_path = "frontend/data/child_photo_02.png"
        reference_image = Image.open(ref_image_path)
                
        prompts = [
            #"A child is sitting at the steering wheel inside a BMW car, mirror the image from left to right",
            #       "A child is standing beside a blue BMW car in a parking lot.",
                   "A child meets with a friendly dragon in a magical forest",
                   "A child meets with a witch - old women with long hair, pointed noses, warts, claws, and hunched backs cooking in a pot"]
        
        for index, prompt in enumerate(prompts):
            print(f"Prompt: '{prompt}', index:{index}")
        
            image_data = await generate_image_bytes(prompt, reference_image, high_quality=True)
        
            output_path = f"test_image_output{index}.png"
            with open(output_path, "wb") as f:
                f.write(image_data)
        
            print(f"\n✅ SUCCESS: Image saved to '{output_path}' in your project root.")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
            

if __name__ == "__main__":
    load_dotenv() # Looks for .env in the current directory (project root)
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    asyncio.run(main())