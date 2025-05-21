# Groq API Chainlit Chatbot with Memory

This is a web application built with Python, Chainlit, and the Groq API. It allows users to interact with a Groq language model, featuring chat history and contextual retrieval using a local vector database.

## Features

*   Interactive chat interface using Chainlit.
*   Powered by the Groq API (specifically the `llama3-8b-8192` model).
*   **Chat History:** Remembers the conversation within the current session.
*   **Contextual Retrieval:** Stores conversation history in a local ChromaDB vector database (`./chroma_db` directory) and retrieves relevant past interactions to provide more contextually aware responses.

## Prerequisites

*   Python 3.7+
*   Access to the Groq API and a Groq API key.

## Setup

1.  **Clone the repository (if applicable) or download the `app.py`, `vector_utils.py`, and `requirements.txt` files.**

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    The `requirements.txt` file includes all necessary packages:
    ```bash
    pip install -r requirements.txt
    ```
    This will install `chainlit`, `groq`, `chromadb`, `sentence-transformers`, and their dependencies.

4.  **Set the Groq API Key:**
    You need to set your Groq API key as an environment variable named `GROQ_API_KEY`.
    
    On Linux/macOS:
    ```bash
    export GROQ_API_KEY='your_actual_api_key_here'
    ```
    On Windows (Command Prompt):
    ```bash
    set GROQ_API_KEY=your_actual_api_key_here
    ```
    Replace `your_actual_api_key_here` with your real Groq API key.

## Running the Application

1.  Ensure your virtual environment is activated and the `GROQ_API_KEY` is set.

2.  Run the Chainlit application using the following command:
    ```bash
    chainlit run app.py -w
    ```
    The `-w` flag enables auto-reloading. The first time you run it, and as you chat, a `./chroma_db` directory will be created in the same location as `app.py` to store the vector database.

3.  Open your web browser and navigate to the address provided by Chainlit (usually `http://localhost:8000`).

## How it Works

*   **Chainlit Interface:** `app.py` uses Chainlit to manage the UI and user interactions.
*   **Chat History:** User and bot messages are stored in the Chainlit user session for the duration of the session.
*   **Vector Database (`vector_utils.py` & ChromaDB):**
    *   The `vector_utils.py` file contains helper functions to interact with ChromaDB.
    *   A persistent ChromaDB instance is initialized in the `./chroma_db` directory.
    *   Each user query and the corresponding bot response are combined and stored as a document in the "chat_history" collection within ChromaDB. This uses sentence transformers (e.g., `all-MiniLM-L6-v2`) to create embeddings for the text.
*   **Message Processing (`app.py` - `on_message`):**
    1.  The user's message is added to the session's chat history.
    2.  The message is used to query ChromaDB (via `vector_utils.py`) to find relevant past interactions (documents).
    3.  A prompt is constructed for the Groq API, including a system message, the recent chat history, and the retrieved context from ChromaDB.
    4.  The Groq API processes this prompt and returns a response.
    5.  The user's message and the bot's response are then stored in ChromaDB for future reference.
    6.  The bot's response is displayed to the user.
*   A welcome message is displayed when the chat session starts, handled by `on_chat_start` in `app.py`.
