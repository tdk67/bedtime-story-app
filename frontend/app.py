import streamlit as st
import yaml
import requests
import base64

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
if 'history' not in st.session_state:
    st.session_state.history = []
if 'audio_to_play' not in st.session_state:
    st.session_state.audio_to_play = None

# --- UI Elements ---
# This placeholder will be used to play audio clips without disrupting the layout
audio_placeholder = st.empty()

# If an audio clip is scheduled to play, render it here and reset
if st.session_state.audio_to_play:
    audio_placeholder.audio(st.session_state.audio_to_play, format='audio/mp3', autoplay=True)
    st.session_state.audio_to_play = None

# --- API Call Functions ---
def get_story_start():
    response = requests.post(f"{BACKEND_URL}/start_story", json={"config": config})
    response.raise_for_status()
    return response.json()

def get_story_next(history, choice):
    response = requests.post(
        f"{BACKEND_URL}/next_step",
        json={"conversation_history": history, "choice": choice, "config": config}
    )
    response.raise_for_status()
    return response.json()

# --- UI Views ---
if st.session_state.view == 'intro':
    try:
        with open(config['intro_video_path'], 'rb') as video_file:
            video_bytes = video_file.read()
            st.video(video_bytes)
    except FileNotFoundError:
        st.warning(f"Intro video not found at: {config['intro_video_path']}")

    if st.button("Let's start the adventure!"):
        with st.spinner("Our storyteller is getting ready..."):
            try:
                story_data = get_story_start()
                st.session_state.history = [story_data]
                st.session_state.view = 'story'
                # Schedule the main narration audio to play automatically
                st.session_state.audio_to_play = base64.b64decode(story_data['narration_audio_b64'])
                st.rerun()
            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to the story engine. Is the backend running? Error: {e}")

elif st.session_state.view == 'story':
    # Display the full story history from the session state
    for entry in st.session_state.history:
        st.markdown(entry['story_text'])
    
    # Get the most recent story segment to work with
    current_segment = st.session_state.history[-1]
    
    # Check if the story has ended
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
        
        # Display the choices with replay buttons
        for choice in current_segment['choices']:
            col1, col2 = st.columns([0.85, 0.15])
            
            with col1:
                # Button to select a choice and continue the story
                if st.button(choice['text'], key=f"choice_{choice['text']}"):
                    with st.spinner("Turning the page..."):
                        next_segment = get_story_next(
                            current_segment['conversation_history'],
                            choice['text']
                        )
                        st.session_state.history.append(next_segment)
                        # Schedule the next segment's main narration to play
                        st.session_state.audio_to_play = base64.b64decode(next_segment['narration_audio_b64'])
                        st.rerun()
            with col2:
                # Button to replay the audio for this specific choice
                if st.button("🔊", key=f"play_{choice['text']}"):
                    st.session_state.audio_to_play = base64.b64decode(choice['audio_b64'])
                    st.rerun()