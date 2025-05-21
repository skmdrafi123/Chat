import chainlit as cl
import os
from groq import Groq

@cl.on_chat_start
async def on_chat_start():
    """
    Sends a welcome message when the chat starts.
    """
    await cl.Message(content="Welcome to the Groq-powered Chatbot! How can I help you today?").send()

@cl.on_message
async def on_message(message: cl.Message):
    """
    Handles incoming messages from the user.
    Retrieves the Groq API key, initializes the Groq client,
    makes a chat completion request, and sends the response back to the user.
    """
    api_key = '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'

    if not api_key:
        await cl.Message(content="GROQ_API_KEY environment variable not set. Please set it and try again.").send()
        return

    client = Groq(api_key=api_key)

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message.content,
                }
            ],
            model="llama3-8b-8192",
        )
        await cl.Message(content=chat_completion.choices[0].message.content).send()
    except Exception as e:
        await cl.Message(content=f"An error occurred: {str(e)}").send()
