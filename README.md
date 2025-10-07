# ✨ Story Weaver: An Interactive AI Storyteller

Story Weaver is a project aimed at creating a personalized, interactive, and co-creative storytelling experience for children. The core idea is to move beyond passive story generation and empower a child to become the author and hero of their own adventure.

This application leverages Large Language Models (LLMs) to craft unique, branching fairy tales. It features a fully asynchronous backend to generate story text, images, and audio in parallel for a seamless user experience. The story prompts are carefully engineered to create exciting adventures with safe tension, where the hero always wins through cleverness and friendship, never violence.

## 🧠 Core Architecture

To create a seamless and responsive experience, Story Weaver uses several key patterns:

1.  **Asynchronous Backend**: The FastAPI backend uses `asyncio` to run all slow AI generation tasks (text, multiple images, and audio) concurrently. This drastically reduces the total generation time for each story segment.
2.  **Frontend Pre-generation**: When a story page is displayed, the frontend immediately starts generating all possible next steps in the background. When the user makes a choice, the content is already prepared, making the transition feel instantaneous.
3.  **Fire and Poll**: The frontend communicates with the backend by "firing" a generation request to get a `job_id`, and then "polling" a status endpoint until the job is complete, at which point it fetches the final result.

---

## 🏗️ Project Structure

The application is split into a **backend** (the engine), a **frontend** (the user interface), and a **test suite**.

```
story_weaver/
├── .env
├── backend/
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── config.py           # Loads and validates the generation config
│   │   └── generators.py       # All AI generation logic (text, audio, image)
│   ├── generation_config.yaml  # Config for AI models and story prompts
│   └── main.py                 # FastAPI server, endpoints, and orchestration
├── frontend/
│   ├── config.yaml             # Config for the child's personalization details
│   ├── intro.html              # The starting page of the application
│   ├── index.html              # The main story and choices page
│   └── data/                   # Local assets (videos, images, etc.)
└── tests/
    ├── __init__.py
    └── backend/
        ├── __init__.py
        ├── test_asyncio.py
        ├── test_audio_generator.py
        ├── test_image_generator.py
        ├── test_interactive_story.py
        └── test_text_generator.py
```

---

## ⚙️ Installation and Setup

### 1. Prerequisites

* **Python 3.8+**
* **Git**
* A modern **Web Browser**

### 2. Clone and Set Up

```bash
git clone <your-repository-url>
cd story-weaver
```

### 3. Install Backend Dependencies

```bash
# From the root story_weaver/ folder:
cd backend
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
cd .. 
```

### 4. Set Up Your API Keys

Place your API keys from OpenAI and Google in a `.env` file in the project's root directory.

**.env**
```
OPENAI_API_KEY="sk-YourSecretOpenAIApiKeyGoesHere"
GOOGLE_API_KEY="YourSecretGoogleApiKeyGoesHere"
```

### 5. Personalize the Story (Two Locations)

Configuration is split into two files for clarity:

* **A. Child's Details:** Edit `frontend/config.yaml` to add the child's name, age, and other personal details that will be woven into the story.
* **B. Story & AI Configuration:** Edit `backend/generation_config.yaml` to change the core story prompt, adjust the fairy tale theme, or update the AI model names.

---

## 🚀 Usage (Running the App)

You need to run the backend and frontend separately.

### Step 1: Run the Backend Server

In a terminal, navigate to the `backend` folder and start the FastAPI server.
```bash
cd backend
# Make sure your backend virtual environment is activated
uvicorn main:app --reload
```
The server will run at `http://127.0.0.1:8000`. Keep this terminal open.

### Step 2: Open the Frontend

Navigate to the `frontend` folder in your file explorer and **double-click the `intro.html` file** to open it in your web browser.

---

## 🧪 Testing the Application

A test suite is included to let you test individual parts of the AI generation without running the full application.

### How to Run Tests

All test commands must be run from the **project's root directory (`story_weaver/`)**.

```bash
# Navigate to the project root
cd path/to/your/story_weaver

# Make sure your backend virtual environment is activated
source backend/venv/bin/activate 
```

Then, run any of the test scripts as a module using the `python -m` flag:

### Available Tests

* **Test Image Generation**
    * Generates a sample image and saves it as `test_image_output.png`.
    * **Command:** `python -m tests.backend.test_image_generator`

* **Test Audio Generation**
    * Generates a sample audio clip and saves it as `test_audio_output.mp3`.
    * **Command:** `python -m tests.backend.test_audio_generator`

* **Test Text Generation**
    * Prints a single generated story segment to the console.
    * **Command:** `python -m tests.backend.test_text_generator`

* **Interactive Story Test**
    * Starts a full, interactive story session in your terminal.
    * **Command:** `python -m tests.backend.test_interactive_story`

* **Async Showcase Test**
    * Demonstrates how `asyncio.gather` works and handles exceptions.
    * **Command:** `python -m tests.backend.test_asyncio --fail-mode <mode>`
    * (Replace `<mode>` with `none`, `robust`, or `fail_fast`)