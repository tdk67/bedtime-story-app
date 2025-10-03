import streamlit as st
import yaml
import requests
import base64
import time
from io import BytesIO
from PIL import Image

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000"
try:
    with open("config.yaml", 'r') as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    st.error("Error: config.yaml not found. Please create it.")
    st.stop()

st.set_page_config(page_title="Story Weaver", layout="wide")
st.title("✨ Welcome to Story Weaver ✨")

# --- Session State Initialization ---
if 'view' not in st.session_state:
    st.session_state.view = 'intro'
if 'history' not in st.session_state:
    st.session_state.history = []
if 'audio_to_play' not in st.session_state:
    st.session_state.audio_to_play = None
if 'pregen_jobs' not in st.session_state:
    st.session_state.pregen_jobs = {}

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
    if not st.session_state.pregen_jobs.get('intro_job'):
        st.session_state.pregen_jobs['intro_job'] = trigger_generation()
    vid_col, _ = st.columns([2, 1]) 
    with vid_col:
        try:
            with open(config['intro_video_path'], 'rb') as video_file:
                video_bytes = video_file.read()
                st.video(video_bytes)
        except FileNotFoundError:
            st.warning(f"Intro video not found at: {config['intro_video_path']}")
    if st.button("Let's start the adventure!"):
        with st.spinner("The first page of our story is being drawn..."):
            job_id = st.session_state.pregen_jobs.get('intro_job')
            story_data = poll_for_result(job_id)
            if story_data:
                st.session_state.history = [story_data]
                st.session_state.view = 'story'
                st.session_state.audio_to_play = base64.b64decode(story_data['narration_audio_b64'])
                st.session_state.pregen_jobs = {}
                st.rerun()

elif st.session_state.view == 'story':
    current_segment = st.session_state.history[-1]
    main_col, options_col = st.columns([0.6, 0.4])

    with main_col:
        if current_segment.get('main_illustration_b64'):
            try:
                image_data = base64.b64decode(current_segment['main_illustration_b64'])
                img = Image.open(BytesIO(image_data))
                img.thumbnail((700, 700))
                # --- FIX: Display the image at its actual resized dimensions ---
                st.image(img) 
            except Exception as e:
                st.error("Could not display the main illustration.")
                print(e)
        st.markdown("---")
        st.markdown(f"### {current_segment['story_text']}")

    with options_col:
        st.write("#### What should we do next?")
        st.markdown("---")
        if not st.session_state.pregen_jobs and current_segment['choices']:
            for choice in current_segment['choices']:
                st.session_state.pregen_jobs[choice['text']] = trigger_generation(
                    current_segment['conversation_history'], choice['text']
                )
        if not current_segment['choices']:
            st.balloons()
            st.success("The End!")
            # --- FIX: Address deprecation warning for button ---
            if st.button("Start a New Adventure?", use_container_width=True):
                st.session_state.view = 'intro'
                st.session_state.history = []
                st.session_state.pregen_jobs = {}
                st.rerun()
        else:
            for choice in current_segment['choices']:
                job_id = st.session_state.pregen_jobs.get(choice['text'])
                status = get_status(job_id)
                if choice.get('image_b64'):
                    try:
                        choice_img_data = base64.b64decode(choice['image_b64'])
                        choice_img = Image.open(BytesIO(choice_img_data))
                        choice_img.thumbnail((250, 250))
                        # --- FIX: Display the image at its actual resized dimensions ---
                        st.image(choice_img)
                    except Exception as e:
                         st.write(f"*{choice['text']}*")
                         print(f"Error displaying choice image: {e}")
                
                # --- FIX: Address deprecation warning for button ---
                if st.button(choice['text'], key=f"choice_{choice['text']}", use_container_width=True):
                    with st.spinner("Turning the page..."):
                        next_segment = poll_for_result(job_id)
                        if next_segment:
                            st.session_state.history.append(next_segment)
                            st.session_state.audio_to_play = base64.b64decode(next_segment['narration_audio_b64'])
                            st.session_state.pregen_jobs = {}
                            st.rerun()
                if status != 'complete':
                     st.spinner("")
                st.markdown("---")