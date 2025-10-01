# ✨ Story Weaver: An Interactive AI Storyteller

Story Weaver is a project aimed at creating a personalized, interactive, and co-creative storytelling experience for children. The core idea is to move beyond passive story generation and empower a child to become the author and hero of their own adventure.

This application is built on a "Safety-by-Design" framework, ensuring that every story is a positive, gentle, and reassuring experience appropriate for bedtime. By leveraging a powerful Large Language Model (LLM), Story Weaver crafts unique, branching narratives that incorporate a child's personal details—like their name, favorite color, and favorite activities—directly into the plot.

## 🧠 Asynchronous Generation Logic

To create a seamless and responsive experience, Story Weaver uses an asynchronous "Fire and Poll" pattern to generate story segments. This significantly reduces the perceived waiting time for the user.

1.  **Fire (Trigger Generation)**: As soon as possible (e.g., while the intro video is playing), the frontend sends a quick request to the backend to start generating the next story segment(s). The backend immediately returns a unique `job_id` and begins the slow AI generation process in the background.

2.  **Pre-generation**: This pattern is used to get a head start. While the user listens to the current story part, the app is already generating all possible next steps in the background.

3.  **Poll (Check Status)**: When the user makes a choice, the frontend uses the corresponding `job_id` to ask the backend's status endpoint, "Is the story ready yet?".

4.  **Fetch (Get Result)**: Once the backend confirms the generation is complete, the frontend makes one final call to retrieve the finished story text and audio. This makes the transition between story parts feel almost instantaneous.

---

## 🏗️ Project Structure

The application is now split into a **backend** (the engine) and a **frontend** (the user interface).

```
story_weaver/
├── .env                  # Securely stores your API key
├── backend/
│   ├── main.py           # The FastAPI server, API endpoints, and AI logic
│   └── requirements.txt  # Python libraries for the backend
└── frontend/
    ├── app.py            # The Streamlit user interface code
    ├── config.yaml       # Personalization details for the child's story
    ├── data/
    │   └── intro.mp4     # The introductory video file
    └── requirements.txt  # Python libraries for the frontend
```

---

## ⚙️ Installation and Setup

### 1. Prerequisites

* **Python 3.8+**
* **Git**

### 2. Clone and Set Up

```bash
git clone <your-repository-url>
cd story-weaver
```

### 3. Install Dependencies (Two Steps)

This project has separate dependencies for the backend and frontend. You'll need to run `pip install` in each folder.

**A. Install Backend Dependencies:**
```bash
# From the root story_weaver/ folder:
cd backend
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
cd .. 
```

**B. Install Frontend Dependencies:**
```bash
# From the root story_weaver/ folder:
cd frontend
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
cd ..
```

### 4. Get Your API Key

Get your API key from the [OpenAI Platform](https://platform.openai.com/api-keys) and place it in a `.env` file in the project's root directory.

**.env**
```
OPENAI_API_KEY="sk-YourSecretApiKeyGoesHere"
```

### 5. Personalize the Story

Edit `frontend/config.yaml` to add the child's details and configure the intro video and voice.

---

## 🚀 Usage (Running the App)

Because the app is now two separate parts, you need to run them in **two separate terminals**.

### Terminal 1: Run the Backend

Navigate to the `backend` folder and start the FastAPI server.
```bash
cd backend
# Make sure your backend virtual environment is activated
uvicorn main:app --reload
```
The server will be running at `http://127.0.0.1:8000`.

### Terminal 2: Run the Frontend

Navigate to the `frontend` folder and run the Streamlit app.
```bash
cd frontend
# Make sure your frontend virtual environment is activated
streamlit run app.py
```
Your web browser will open with the Story Weaver application.

---

## 🛠️ Technology Stack

#### Backend
* **FastAPI**: A modern, high-performance web framework for building the API.
* **Uvicorn**: A lightning-fast server to run the FastAPI application.
* **OpenAI**: The official Python library for interacting with the GPT and TTS models.
* **Python-dotenv**: For securely managing the API key.

#### Frontend
* **Streamlit**: A Python library used to create the simple, interactive web-based user interface.
* **Requests**: A library for making HTTP requests from the frontend to the backend API.
* **PyYAML**: For reading the `config.yaml` file.

---

## 🗺️ Future Roadmap

* **Phase 2: Adding Visuals**: Integrate an image generation model to create illustrations for each story segment, with a focus on creating a *consistent character*.
* **Phase 3: Voice Input**: Implement Speech-to-Text to allow the child to speak their choices instead of clicking buttons.