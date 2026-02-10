import asyncio
import os
import base64
import wave
from openai import AsyncOpenAI
from dotenv import load_dotenv

async def generate_audio_stream_openrouter(client, text, voice="onyx"):
    # We use a strict system message to force 'Narrator Mode'
    stream = await client.chat.completions.create(
        model="openai/gpt-4o-audio-preview",
        modalities=["text", "audio"],
        audio={"voice": voice, "format": "pcm16"},
        messages=[
            {
                "role": "system", 
                "content": "You are a professional narrator. Your ONLY task is to read the provided text aloud. Do NOT add any introductory remarks, commentary, or conversational responses. Read the text exactly as written."
            },
            {
                "role": "user", 
                "content": f"Please narrate this text: {text}"
            }
        ],
        stream=True
    )

    full_audio_base64 = ""
    async for chunk in stream:
        if not chunk.choices: continue
        delta = chunk.choices[0].delta
        if hasattr(delta, 'audio') and delta.audio and 'data' in delta.audio:
            full_audio_base64 += delta.audio['data']

    if not full_audio_base64:
        raise Exception("No audio data received.")

    return base64.b64decode(full_audio_base64)

async def main():
    print("--- Testing OpenRouter Audio (Strict Narrator Mode) ---")
    load_dotenv()
    client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))

    try:
        text = "Hello, this is a test of the text to speech system. I am reading this exactly as it is written."
        audio_bytes = await generate_audio_stream_openrouter(client, text)
        
        output_path = "playable_story.wav"
        with wave.open(output_path, "wb") as wav_file:
            # Set the 'passport' for the raw data
            # (nchannels, sampwidth, framerate, nframes, comptype, compname)
            # 1 = Mono, 2 = 16-bit (2 bytes), 24000 = Sample Rate
            wav_file.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
            wav_file.writeframes(audio_bytes)

        print(f"✅ Success! Saved as standard WAV: {output_path}")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())