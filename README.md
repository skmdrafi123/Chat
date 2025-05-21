# Groq API Chainlit Chatbot

This is a simple web application built with Python, Chainlit, and the Groq API. It allows users to interact with a Groq language model through a chat interface.

## Prerequisites

*   Python 3.7+
*   Access to the Groq API and a Groq API key.

## Setup

1.  **Clone the repository (if applicable) or download the files.**

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

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
    The `-w` flag enables auto-reloading, which is helpful during development.

3.  Open your web browser and navigate to the address provided by Chainlit (usually `http://localhost:8000`).

## How it Works

*   The application uses Chainlit to create the user interface.
*   When a user sends a message, it's processed by the `on_message` function in `app.py`.
*   This function calls the Groq API using the `groq` Python client and the `llama3-8b-8192` model.
*   The response from the Groq API is then displayed to the user in the chat interface.
*   A welcome message is displayed when the chat session starts.
