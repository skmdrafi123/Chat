import chainlit as cl
import os
from groq import Groq
import uuid # For generating unique IDs for documents

# Attempt to import vector_utils, handle if not found for robustness
try:
    import vector_utils
except ImportError:
    vector_utils = None # Allows app to at least start and report missing util

# Constants
GROQ_MODEL = "llama3-8b-8192"
VECTOR_DB_COLLECTION_NAME = "chat_history"
VECTOR_DB_PATH = "./chroma_db" # Path for ChromaDB persistent storage

@cl.on_chat_start
async def on_chat_start():
    """
    Initializes chat history, Groq client, vector DB client, and embedding function.
    Displays a welcome message.
    """
    if vector_utils is None:
        await cl.Message(content="Error: vector_utils.py is missing. Vector search functionality will be disabled.").send()
        # Optionally, you could prevent the chat from starting or run in a degraded mode.
        # For now, it will likely fail later when trying to use db_client or embed_fn.
    
    # Initialize chat history in the user session
    cl.user_session.set("history", [])
    
    # Initialize Groq client (API key check will be done in on_message)
    # No need to store it in user_session if it's re-created per message based on env var

    # Initialize vector database client and embedding function
    try:
        db_client = vector_utils.init_db(path=VECTOR_DB_PATH, collection_name=VECTOR_DB_COLLECTION_NAME)
        cl.user_session.set("db_client", db_client)
        
        # The embedding function is managed by vector_utils.init_db ensuring the collection has one.
        # No need to explicitly get/set it here unless used directly in app.py, which it isn't.
        # embed_fn = vector_utils.get_embedding_function() 
        # cl.user_session.set("embed_fn", embed_fn) 

    except Exception as e:
        await cl.Message(content=f"Error initializing vector database: {str(e)}. Retrieval functionality may be affected.").send()
        cl.user_session.set("db_client", None) # Ensure it's None if init fails

    await cl.Message(content="Welcome to the Enhanced Groq Chatbot! I now remember our conversation and can use past context. How can I help?").send()

@cl.on_message
async def on_message(message: cl.Message):
    """
    Handles incoming messages:
    1. Retrieves history, API key, and DB client.
    2. Appends user message to history.
    3. Queries vector DB for relevant context.
    4. Constructs a prompt with history, context, and current message.
    5. Sends prompt to Groq API.
    6. Stores user message and bot response in vector DB.
    7. Appends bot response to history.
    8. Sends response to user.
    """
    history = cl.user_session.get("history")
    db_client = cl.user_session.get("db_client")
    # embed_fn = cl.user_session.get("embed_fn") # Not directly used here if collection handles it

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        await cl.Message(content="GROQ_API_KEY environment variable not set. Please set it and try again.").send()
        return

    if vector_utils is None:
        await cl.Message(content="Critical Error: vector_utils.py is missing. Cannot proceed.").send()
        return
        
    if db_client is None:
        await cl.Message(content="Error: Vector database client is not available. Retrieval functionality is disabled.").send()
        # Proceed without vector search or return, depending on desired behavior
        # For now, we'll try to proceed without retrieval

    # 1. Append user message to history
    history.append({"role": "user", "content": message.content})

    # 2. Query vector DB for relevant context
    context_str = ""
    if db_client: # Only query if db_client is available
        try:
            relevant_docs = vector_utils.query_collection(
                client=db_client,
                collection_name=VECTOR_DB_COLLECTION_NAME,
                query_text=message.content,
                n_results=2  # Get top 2 relevant docs
            )
            if relevant_docs:
                context_str = "Relevant past context:\n" + "\n".join([f"- {doc}" for doc in relevant_docs])
                # print(f"Retrieved context: {context_str}") # For debugging
        except Exception as e:
            # print(f"Error querying vector DB: {str(e)}") # For debugging
            await cl.Message(content=f"Notice: Could not retrieve context from vector database: {str(e)}").send()


    # 3. Construct messages for Groq API
    # System prompt can guide the model on how to use history and context
    system_prompt = "You are a helpful assistant. Use the provided chat history and relevant context to answer the user's current question or statement. Be concise and helpful."
    
    groq_messages = [{"role": "system", "content": system_prompt}]

    # Add chat history (e.g., last N messages to keep prompt size manageable)
    MAX_HISTORY_MESSAGES = 5 
    for hist_msg in history[-(MAX_HISTORY_MESSAGES*2):]: # User and Bot messages
        groq_messages.append(hist_msg)

    # Add retrieved context if available
    if context_str:
        groq_messages.append({"role": "system", "content": "Consider the following relevant context from past interactions (do not mention it directly unless asked about past conversations):\n" + context_str})
    
    # Add current user message (it's already in history, but explicit here for clarity before API call)
    # Actually, it's better to ensure the history added above is the source of truth.
    # The last message in `history` is the current user message.

    # Initialize Groq client
    client = Groq(api_key=api_key)

    try:
        # 4. Send prompt to Groq API
        chat_completion = client.chat.completions.create(
            messages=groq_messages, # Pass the constructed list of messages
            model=GROQ_MODEL,
        )
        bot_response_content = chat_completion.choices[0].message.content

        # 5. Store user message and bot response in vector DB (if db_client is available)
        if db_client:
            try:
                interaction_text = f"User: {message.content}\nBot: {bot_response_content}"
                vector_utils.add_text_to_collection(
                    client=db_client,
                    collection_name=VECTOR_DB_COLLECTION_NAME,
                    text=interaction_text,
                    doc_id=str(uuid.uuid4()) # Ensure unique ID for each interaction
                )
                # print(f"Stored interaction: {interaction_text}") # For debugging
            except Exception as e:
                # print(f"Error storing interaction in vector DB: {str(e)}") # For debugging
                await cl.Message(content=f"Notice: Could not store this interaction in the vector database: {str(e)}").send()


        # 6. Append bot response to history
        history.append({"role": "assistant", "content": bot_response_content})
        cl.user_session.set("history", history) # Update history in session

        # 7. Send response to user
        await cl.Message(content=bot_response_content).send()

    except Exception as e:
        # print(f"Error calling Groq API: {str(e)}") # For debugging
        await cl.Message(content=f"An error occurred with the Groq API: {str(e)}").send()
