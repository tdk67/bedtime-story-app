import streamlit as st
import yaml
import openai
import os
import re
from dotenv import load_dotenv

# --- DOTENV SETUP ---
load_dotenv()

# --- CONFIGURATION ---
try:
    with open("config.yaml", 'r') as file:
        config = yaml.safe_load(file)
    child_info = config.get("child_info", {})
    personalization = config.get("personalization", {})
except FileNotFoundError:
    st.error("Error: config.yaml not found. Please create it.")
    st.stop()

# --- LLM SETUP ---
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file or environment.")
    client = openai.OpenAI(api_key=api_key)
except Exception as e:
    st.error(f"Failed to initialize OpenAI client. Is your OPENAI_API_KEY set in the .env file? Error: {e}")
    st.stop()


def get_story_prompt():
    """
    This function generates the master "system prompt" for the AI storyteller.
    """
    personalization_details = ", ".join(
        f"{key.replace('_', ' ')} is {value}"
        for key, value in personalization.items()
        if value is not None
    )

    prompt = f"""
    You are a world-class bedtime storyteller for a {child_info.get('age', 6)}-year-old child named {child_info.get('name', 'Friend')}.
    Your primary goal is to create a gentle, interactive, and personalized story that always ends happily and teaches a positive lesson.

    **STORY RULES:**
    1.  **Main Character:** The main character is ALWAYS {child_info['name']}. Refer to the main character as {child_info['name']}.
    2.  **Personalization:** Seamlessly weave these personal details into the story: {personalization_details}.
    3.  **Tone:** Keep the tone calm, positive, and reassuring. Absolutely NO scary, violent, or sad themes. This is a bedtime story.
    4.  **Structure:** Narrate the story in short segments (3-4 sentences). At the end of EACH segment, you MUST ask a question with 2 or 3 clear choices.
    5.  **Choice Format:** Present the choices clearly using bracketed format, like this: [Choice 1] or [Choice 2]. Do not use any other format.
    6.  **Pacing:** The entire story must conclude in 5 to 8 steps (question-answer cycles). Guide the narrative towards a happy ending within this timeframe.
    7.  **Moral:** The story must have a clear, simple, and positive moral lesson, like "sharing is caring," "kindness is magical," or "it's brave to try new things".
    8.  **Happy Ending:** The story MUST have a happy and satisfying conclusion. This is non-negotiable.

    **INITIAL TASK:**
    Do not start the story yet. Your first task is to help {child_info['name']} choose an adventure.
    Ask a single, imaginative question with three choices. Each choice should subtly lead to one of these classic fairy tale themes:
    - The Three Little Pigs (building, being clever)
    - Little Red Riding Hood (helping family, being cautious)
    - Jack and the Beanstalk (adventure, magic, being brave)
    - The Tortoise and the Hare (persistence, not giving up)
    - Goldilocks and the Three Bears (curiosity, respecting others' things)

    Frame the question creatively. For example: "If you found a magical box, what would you wish to find inside? [A set of magical building blocks], [A map to a secret garden], or [A tiny, talking animal friend]?"
    Wait for the user's response before you begin the story.
    """
    return prompt

def get_ai_response(messages):
    """
    Sends the conversation history to the AI and gets the next part of the story.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred while communicating with the AI: {e}")
        return "Oh dear, my book of stories seems to be stuck. Let's try again in a moment."

def parse_story_and_choices(response_text):
    """
    Uses regular expressions to find the story part and the choices from the AI's response.
    """
    choices = re.findall(r'\[(.*?)\]', response_text)
    story_part = re.split(r'\[', response_text)[0].strip()
    is_the_end = "the end" in story_part.lower() and not choices
    return story_part, choices, is_the_end

# --- STREAMLIT UI ---

st.set_page_config(page_title=f"{child_info.get('name', 'My')}'s Story Weaver", layout="centered")
st.title(f"✨ Welcome to {child_info.get('name', 'Your')}'s Story Weaver ✨")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'story_started' not in st.session_state:
    st.session_state.story_started = False
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

# This loop now handles ALL story text rendering.
# It iterates through the history and builds the storybook chronologically.
if st.session_state.story_started:
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            story_part, _, _ = parse_story_and_choices(message["content"])
            st.markdown(story_part)

# Main application logic
if not st.session_state.game_over:
    if not st.session_state.story_started:
        # Start the story on the first run
        st.session_state.messages.append({"role": "system", "content": get_story_prompt()})
        st.session_state.messages.append({"role": "user", "content": "Let's begin the story."})
        
        with st.spinner("Thinking of a magical adventure..."):
            initial_response = get_ai_response(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": initial_response})
        
        st.session_state.story_started = True
        st.rerun()

    else:
        # Get the latest response to parse for choices
        last_response = st.session_state.messages[-1]["content"]
        _, choices, is_the_end = parse_story_and_choices(last_response)
        
        # --- BUG FIX ---
        # The redundant st.markdown(story_part) call that was here has been REMOVED.
        # The loop at the top of the UI section now handles all rendering.
        
        if is_the_end:
            st.balloons()
            st.markdown("### The End")
            st.session_state.game_over = True
        else:
            # Display choices as buttons. This is the only UI rendered in this block.
            cols = st.columns(len(choices))
            for i, choice in enumerate(choices):
                # Using a unique key for each button to ensure stability
                if cols[i].button(choice, key=f"choice_{i}"):
                    st.session_state.messages.append({"role": "user", "content": choice})
                    with st.spinner("Turning the page..."):
                        new_story_part = get_ai_response(st.session_state.messages)
                        st.session_state.messages.append({"role": "assistant", "content": new_story_part})
                    st.rerun()

# Offer a way to restart the story
if st.session_state.game_over:
    if st.button("Start a New Adventure?"):
        # Reset the session state
        st.session_state.messages = []
        st.session_state.story_started = False
        st.session_state.game_over = False
        st.rerun()