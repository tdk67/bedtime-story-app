import asyncio
import os
import base64
from PIL import Image
import io
from dotenv import load_dotenv
from openai import OpenAI

def image_to_base64_url(image_path):
    with open(image_path, "rb") as image_file:
        base64_data = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:image/png;base64,{base64_data}"

async def generate_consistent_image(client, prompt, ref_image_path):
    # Convert local image to base64 Data URL for OpenRouter
    ref_image_url = image_to_base64_url(ref_image_path)
    
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash-image",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Using the character in this image: {prompt}"},
                    {"type": "image_url", "image_url": {"url": ref_image_url}}
                ]
            }
        ],
        modalities=["image"] # Vital for triggering image output
    )

    resp_dict = response.model_dump()
    for choice in resp_dict.get("choices", []):
        images = choice.get("message", {}).get("images", [])
        if images:
            # Handle both 'url' and nested 'image_url.url' formats
            img_url = images[0].get("url") or images[0].get("image_url", {}).get("url")
            return base64.b64decode(img_url.split("base64,")[1])
            
    raise Exception("Generation failed to return an image.")

async def main():
    load_dotenv()
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
    
    try:
        # Pass the local reference image path
        img_bytes = await generate_consistent_image(
            client, 
            "A child meets with a friendly dragon in a magical forest", 
            "../../frontend/data/child_photo_02.png"
        )
        
        with open("consistent_output.png", "wb") as f:
            f.write(img_bytes)
        print("✅ SUCCESS: Consistent character image saved.")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())