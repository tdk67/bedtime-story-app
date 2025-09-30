# ✨ Story Weaver: An Interactive AI Storyteller

Story Weaver is a project aimed at creating a personalized, interactive, and co-creative storytelling experience for children. [cite_start]The core idea is to move beyond passive story generation and empower a child to become the author and hero of their own adventure[cite: 147, 171].

[cite_start]This application is built on a "Safety-by-Design" framework, ensuring that every story is a positive, gentle, and reassuring experience appropriate for bedtime[cite: 153]. By leveraging a powerful Large Language Model (LLM), Story Weaver crafts unique, branching narratives that incorporate a child's personal details—like their name, favorite color, and favorite activities—directly into the plot.

## Current Version: The Core Text Engine

[cite_start]This initial version represents **Phase 1: The Core Experience**[cite: 76]. We have built the foundational text-based storytelling loop. It's a simple but powerful demonstration of the core mechanics:

* [cite_start]**Deep Personalization**: The story is built around the child's details provided in a simple configuration file[cite: 163].
* [cite_start]**Interactive Branching Narrative**: The child actively directs the story by making choices at key points, transforming them from a listener into a co-creator[cite: 166, 252].
* [cite_start]**Safe & Positive Storytelling**: The AI is guided by a carefully crafted prompt that enforces a calm tone, guarantees a happy ending, and weaves in a gentle moral lesson[cite: 66, 196].
* [cite_start]**Simple Web Interface**: A clean UI built with Streamlit allows for easy testing and interaction[cite: 34].

---

## ⚙️ Installation and Setup

Follow these steps to get the Story Weaver running on your local machine.

### 1. Prerequisites

* **Python 3.8+**: Ensure you have a modern version of Python installed.
* **Git**: Required to clone the repository.

### 2. Clone the Repository

Open your terminal and clone the project files:
```bash
git clone <your-repository-url>
cd story-weaver
```

### 3. Set Up a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.
```bash
# Create the virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```

### 4. Install Dependencies

Install the required Python libraries using the provided `requirements.txt` file (you would create this file with the content `streamlit`, `openai`, `pyyaml`, `python-dotenv`).
```bash
pip install -r requirements.txt
```

### 5. Get Your API Key

This project uses the **OpenAI API** as its story engine.

1.  Go to the [OpenAI Platform website](https://platform.openai.com/api-keys).
2.  Sign up or log in to your account.
3.  Navigate to the API Keys section and create a new secret key.
4.  Copy the key immediately. You won't be able to see it again.

### 6. Configure Your Environment

Create a file named `.env` in the root of your project folder. This file securely stores your API key where the application can access it. Add your key to this file:

**.env**
```
OPENAI_API_KEY="sk-YourSecretApiKeyGoesHere"
```

### 7. Personalize the Story

Open the `config.yaml` file to add the child's details. The `name` and `age` are mandatory, but the more details you provide, the more personalized the story will be.

**config.yaml**
```yaml
child_info:
  name: "Alex"
  age: 6

personalization:
  favourite_colour: "sky blue"
  favourite_food: "strawberry yogurt"
  # ... and other details
```

---

## 🚀 Usage

Once the setup is complete, running the application is simple. Make sure your virtual environment is activated, then run the following command in your terminal:

```bash
streamlit run app.py
```

Your default web browser will open a new tab with the Story Weaver application ready to go!

---

## 🛠️ Technology Stack

* **Streamlit**: A Python library used to create the simple, interactive web-based user interface for testing the story engine.
* [cite_start]**OpenAI API**: The core LLM that serves as the dynamic storyteller, generating narrative segments based on the system prompt and user choices[cite: 287].
* [cite_start]**Python-dotenv**: Used for securely managing the `OPENAI_API_KEY` by loading it from a `.env` file[cite: 44].
* **PyYAML**: A library for reading the `config.yaml` file, which holds all the personalization details for the child.

---

## 🗺️ Future Roadmap

This text-based engine is the foundation. The project roadmap includes exciting next steps to bring the full vision to life:

* [cite_start]**Phase 2: Adding Visuals**: Integrate an image generation model like Stable Diffusion or DALL-E 3 to create illustrations for each story segment[cite: 78, 295]. [cite_start]A key challenge will be creating a *consistent character* based on a child's photo[cite: 80, 301].
* [cite_start]**Phase 3: The Audio Experience**: Implement Speech-to-Text for voice commands and Text-to-Speech for story narration, creating a fully immersive, screen-optional experience[cite: 77, 285, 290].