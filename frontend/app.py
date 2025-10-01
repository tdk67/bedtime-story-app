import streamlit as st
import yaml
import requests
import time

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000"

try:
    with open("config.yaml", 'r') as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    st.error("Error: config.yaml not found. Please create it.")
    st.stop()

st.set_page_config(page_title="Story Weaver", layout="centered")
st.title("✨ Welcome to Story Weaver ✨")

# --- Session State Initialization ---
if 'view' not in st.session_state:
    st.session_state.view = 'intro'
if 'story_data' not in st.session_state:
    st.session_state.story_data = None
if 'history' not in st.session_state:
    st.session_state.history = []

# --- API Call Functions ---
def get_story_start():
    response = requests.post(
        f"{BACKEND_URL}/start_story",
        json={"conversation_history": [], "config": config}
    )
    response.raise_for_status() # Will raise an exception for 4XX/5XX errors
    return response.json()

def get_story_next(history, choice):
    response = requests.post(
        f"{BACKEND_URL}/next_step",
        json={"conversation_history": history, "choice": choice, "config": config}
    )
    response.raise_for_status()
    return response.json()

# --- UI Views ---

# 1. INTRO VIEW
if st.session_state.view == 'intro':
    try:
        video_file = open(config['intro_video_path'], 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)
    except FileNotFoundError:
        st.warning(f"Intro video not found at: {config['intro_video_path']}")

    if st.button("Let's start the adventure!"):
        with st.spinner("Our storyteller is getting ready..."):
            try:
                st.session_state.story_data = get_story_start()
                st.session_state.history.append(st.session_state.story_data)
                st.session_state.view = 'story'
                st.rerun()
            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to the story engine. Is the backend running? Error: {e}")

# 2. STORY VIEW
elif st.session_state.view == 'story':
    # Display the full story history
    for entry in st.session_state.history:
        st.markdown(entry['story_text'])
    
    current_segment = st.session_state.history[-1]
    
    # Auto-play the audio for the latest story part
    if current_segment['story_audio_url']:
        # The autoplay feature can be sensitive in browsers. A small delay can help.
        time.sleep(0.5) 
        st.audio(f"{BACKEND_URL}{current_segment['story_audio_url']}", autoplay=True)

    # Display choices if the story is not over
    if not current_segment['choices']:
        st.balloons()
        st.markdown("### The End")
        if st.button("Start a New Adventure?"):
            st.session_state.view = 'intro'
            st.session_state.history = []
            st.rerun()
    else:
        st.markdown("---")
        st.write("**What should we do next?**")
        
        for choice in current_segment['choices']:
            col1, col2 = st.columns([0.8, 0.2])
            
            with col1:
                if st.button(choice['text'], key=f"choice_{choice['text']}"):
                    with st.spinner("Turning the page..."):
                        try:
                            next_segment = get_story_next(
                                current_segment['conversation_history'],
                                choice['text']
                            )
                            st.session_state.story_data = next_segment
                            st.session_state.history.append(next_segment)
                            st.rerun()
                        except requests.exceptions.RequestException as e:
                            st.error(f"Could not connect to the story engine. Error: {e}")

            with col2:
                if choice['audio_url']:
                    # This button replays the audio for the choice
                    if st.button("🔊", key=f"play_{choice['text']}"):
                        st.audio(f"{BACKEND_URL}{choice['audio_url']}")