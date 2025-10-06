# ✨ Story Weaver: An Interactive AI Storyteller

Story Weaver is a project aimed at creating a personalized, interactive, and co-creative storytelling experience for children. The core idea is to move beyond passive story generation and empower a child to become the author and hero of their own adventure.

This application is built on a "Safety-by-Design" framework, ensuring that every story is a positive, gentle, and reassuring experience appropriate for bedtime. By leveraging a powerful Large Language Model (LLM), Story Weaver crafts unique, branching narratives that incorporate a child's personal details—like their name, favorite color, and favorite activities—directly into the plot.

## 🧠 Asynchronous Generation Logic

To create a seamless and responsive experience, Story Weaver uses an asynchronous "Fire and Poll" pattern to generate story segments. This significantly reduces the perceived waiting time for the user.

1.  **Fire (Trigger Generation)**: As soon as the application's intro page loads, the frontend sends a request to the backend to start generating the first story segment. The backend immediately returns a unique `job_id` and begins the AI generation process in the background.

2.  **Pre-generation**: This pattern is used to get a head start. While the user watches the intro video, the app is already preparing the first part of the story.

3.  **Poll (Check Status)**: The frontend periodically uses the `job_id` to ask the backend's status endpoint, "Is the story ready yet?".

4.  **Fetch (Get Result)**: Once the backend confirms the generation is complete, the frontend makes one final call to retrieve the finished story text, images, and audio. This makes the transition between story parts feel almost instantaneous.

---

## 🏗️ Project Structure

The application is split into a **backend** (the engine) and a **frontend** (the user interface).

```
story_weaver/
├── .env                  # Securely stores your API keys
├── backend/
│   ├── main.py           # The FastAPI server, API endpoints, and AI logic
│   └── requirements.txt  # Python libraries for the backend
└── frontend/
    ├── intro.html        # The starting page of the application
    ├── index.html        # The main story and choices page
    └── data/             # Folder for local assets like videos and images
        ├── background.png
        ├── BedtimeStoryIntro.mp4
        └── child_photo_02.png
```

---

## ⚙️ Installation and Setup

### 1. Prerequisites

* **Python 3.8+**
* **Git**
* A modern **Web Browser** (like Chrome, Firefox, or Safari)

### 2. Clone and Set Up

```bash
git clone <your-repository-url>
cd story-weaver
```

### 3. Install Backend Dependencies

This project only has server-side dependencies for the backend. The frontend runs directly in the browser with no installation needed.

```bash
# From the root story_weaver/ folder:
cd backend
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
cd .. 
```

### 4. Set Up Your API Keys

Get your API keys from the [OpenAI Platform](https://platform.openai.com/api-keys) and the [Google AI Studio](https://aistudio.google.com/app/apikey). Place them in a `.env` file in the project's root directory.

**.env**
```
OPENAI_API_KEY="sk-YourSecretOpenAIApiKeyGoesHere"
GOOGLE_API_KEY="YourSecretGoogleApiKeyGoesHere"
```

### 5. Personalize the Story

All personalization is now done directly in the frontend.

1.  Open the `frontend/intro.html` file.
2.  Find the `<script>` tag at the bottom.
3.  Edit the `storyConfig` JavaScript object with the child's details.

---

## 🚀 Usage (Running the App)

You will need to perform two steps to run the application.

### Step 1: Run the Backend Server

In a terminal, navigate to the `backend` folder and start the FastAPI server.
```bash
cd backend
# Make sure your backend virtual environment is activated
uvicorn main:app --reload
```
The server will be running at `http://12-7.0.0.1:8000`. Keep this terminal open.

### Step 2: Run the Frontend

**There is no command to run.** Simply navigate to the `frontend` folder in your file explorer and **double-click the `intro.html` file** to open it in your web browser.

The story will begin!

---

## 🛠️ Technology Stack

#### Backend
* **FastAPI**: A modern, high-performance web framework for building the API.
* **Uvicorn**: A lightning-fast ASGI server to run the FastAPI application.
* **OpenAI**: The official Python library for interacting with the GPT-4o (text) and TTS (audio) models.
* **Google Generative AI**: The official Python library for interacting with the Gemini model for image generation.
* **Python-dotenv**: For securely managing API keys.

#### Frontend
* **HTML5**: Provides the structure and content of the web pages.
* **CSS3**: Handles all styling, layout, and visual presentation.
* **JavaScript (ES6+)**: Powers the application's interactivity, manages the "Fire and Poll" logic, and communicates with the backend API.

---

## 🗺️ Future Roadmap

* **Phase 2: Voice Input**: Implement Speech-to-Text to allow the child to speak their choices instead of clicking buttons.
* **Phase 3: Character Consistency**: Refine image generation prompts to maintain a more consistent character appearance throughout the story.