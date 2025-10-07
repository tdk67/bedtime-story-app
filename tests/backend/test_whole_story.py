import asyncio
import os
from dotenv import load_dotenv
from openai import OpenAI

# Updated imports to include the shared parsing function
from backend.generation.generators import generate_story_text, get_story_prompt, parse_story_and_choices

async def main():
    """Runs an interactive story session in the terminal."""
    print("--- Starting Interactive Story Generation Test ---")
    
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        mock_app_config = {
            "child_info": {"name": "Marton", "age": 5},
            "personalization": {
                "favourite_animal": "rabbit",
                "favourite_colour": "yellow"
            }
        }
        
        system_prompt = get_story_prompt(mock_app_config)
        history = [{"role": "system", "content": system_prompt}]
        user_message = "Let's begin."

        while True:
            history.append({"role": "user", "content": user_message})

            print("\n\033[93mStory Weaver is thinking...\033[0m")
            assistant_response = await generate_story_text(client, history)
            history.append({"role": "assistant", "content": assistant_response})

            # --- CHANGE: Now using the imported function ---
            narrative, choices = parse_story_and_choices(assistant_response)
            
            print("\n\033[92m" + narrative + "\033[0m")

            if not choices:
                print("\n--- THE END ---")
                break

            print("\nWhat should we do next?")
            for i, choice in enumerate(choices, 1):
                print(f"  {choice}")
            
            while True:
                try:
                    choice_num = int(input("\nChoose your action (enter a number): "))
                    if 1 <= choice_num <= len(choices):
                        user_message = choices[choice_num - 1]
                        break
                    else:
                        print(f"\033[91mInvalid number. Please enter a number between 1 and {len(choices)}.\033[0m")
                except ValueError:
                    print("\033[91mInvalid input. Please enter a number.\033[0m")

    except Exception as e:
        print(f"\n\033[91mAn error occurred: {e}\033[0m")

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())