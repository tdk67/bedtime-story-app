import streamlit as st
import yaml
import requests
import base64
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
if 'history' not in st.session_state:
    st.session_state.history = []
if 'audio_to_play' not in st.session_state:
    st.session_state.audio_to_play = None
if 'pregen_jobs' not in st.session_state:
    st.session_state.pregen_jobs = {} # Stores job IDs for pre-generated choices

# --- UI Elements ---
audio_placeholder = st.empty()
if st.session_state.audio_to_play:
    audio_placeholder.audio(st.session_state.audio_to_play, format='audio/mp3', autoplay=True)
    st.session_state.audio_to_play = None

# --- API Call Functions ---
def trigger_generation(history=None, choice=None):
    payload = {"config": config}
    if history and choice:
        payload["conversation_history"] = history
        payload["choice"] = choice
    
    response = requests.post(f"{BACKEND_URL}/generate/start", json=payload)
    response.raise_for_status()
    return response.json()['job_id']

def get_status(job_id):
    if not job_id: return "not_found"
    response = requests.get(f"{BACKEND_URL}/generate/status/{job_id}")
    response.raise_for_status()
    return response.json()['status']

def poll_for_result(job_id):
    if not job_id:
        st.error("Something went wrong, no job to poll.")
        return None
        
    while True:
        status = get_status(job_id)
        if status == 'complete':
            break
        elif status == 'failed':
            st.error("Story generation failed. Please try again.")
            return None
        time.sleep(1)
    
    response = requests.get(f"{BACKEND_URL}/generate/result/{job_id}")
    response.raise_for_status()
    return response.json()

# --- UI Views ---
if st.session_state.view == 'intro':
    # Pre-generate the first story segment while the video plays
    if not st.session_state.pregen_jobs.get('intro_job'):
        st.session_state.pregen_jobs['intro_job'] = trigger_generation()

    try:
        with open(config['intro_video_path'], 'rb') as video_file:
            video_bytes = video_file.read()
            st.video(video_bytes)
    except FileNotFoundError:
        st.warning(f"Intro video not found at: {config['intro_video_path']}")

    if st.button("Let's start the adventure!"):
        with st.spinner("Story is loading..."):
            job_id = st.session_state.pregen_jobs.get('intro_job')
            story_data = poll_for_result(job_id)
            if story_data:
                st.session_state.history = [story_data]
                st.session_state.view = 'story'
                st.session_state.audio_to_play = base64.b64decode(story_data['narration_audio_b64'])
                st.session_state.pregen_jobs = {} # Clear jobs for the next round
                st.rerun()

elif st.session_state.view == 'story':
    for entry in st.session_state.history:
        st.markdown(entry['story_text'])
    
    current_segment = st.session_state.history[-1]
    
    # --- Pre-generate next steps in the background ---
    if not st.session_state.pregen_jobs and current_segment['choices']:
        for choice in current_segment['choices']:
            st.session_state.pregen_jobs[choice['text']] = trigger_generation(
                current_segment['conversation_history'], choice['text']
            )

    if not current_segment['choices']:
        st.balloons()
        st.markdown("### The End")
        if st.button("Start a New Adventure?"):
            st.session_state.view = 'intro'
            st.session_state.history = []
            st.session_state.pregen_jobs = {}
            st.rerun()
    else:
        st.markdown("---")
        st.write("**What should we do next?**")
        
        for choice in current_segment['choices']:
            job_id = st.session_state.pregen_jobs.get(choice['text'])
            status = get_status(job_id)

            col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
            with col1:
                if st.button(choice['text'], key=f"choice_{choice['text']}"):
                    with st.spinner("Finalizing your choice..."):
                        next_segment = poll_for_result(job_id)
                        if next_segment:
                            st.session_state.history.append(next_segment)
                            st.session_state.audio_to_play = base64.b64decode(next_segment['narration_audio_b64'])
                            st.session_state.pregen_jobs = {} # Clear old jobs
                            st.rerun()
            with col2:
                if st.button("🔊", key=f"play_{choice['text']}"):
                    st.session_state.audio_to_play = base64.b64decode(choice['audio_b64'])
                    st.rerun()
            with col3:
                # Show a polling indicator if the next step is still generating
                if status != 'complete':
                    with st.spinner(""):
                        st.write("") # The spinner itself is the indicator