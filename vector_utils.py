import chromadb
from chromadb.utils import embedding_functions
import uuid

# Global variable for the default embedding function
# This ensures we initialize it only once if needed for multiple utility functions.
DEFAULT_EMBEDDING_FUNCTION = None

def get_embedding_function(model_name="all-MiniLM-L6-v2"):
    """
    Returns a sentence transformer embedding function.
    Initializes DEFAULT_EMBEDDING_FUNCTION if it's not already set.
    """
    global DEFAULT_EMBEDDING_FUNCTION
    if DEFAULT_EMBEDDING_FUNCTION is None:
        DEFAULT_EMBEDDING_FUNCTION = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
    return DEFAULT_EMBEDDING_FUNCTION

def init_db(path="./chroma_db", collection_name="chat_history"):
    """
    Initializes and returns a persistent ChromaDB client.
    Creates the specified collection if it doesn't exist,
    using the default embedding function.
    """
    client = chromadb.PersistentClient(path=path)
    
    # Get the embedding function
    embed_fn = get_embedding_function()
    
    # Check if collection already exists, otherwise create it
    # This is a bit more robust than just calling get_or_create_collection directly
    # without knowing if the embedding function matches if it exists.
    # For simplicity here, we assume if it exists, it's compatible,
    # or we let get_or_create_collection handle it.
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embed_fn
    )
    #print(f"Initialized ChromaDB client. Collection '{collection_name}' is ready.") # For debugging
    return client

def add_text_to_collection(client: chromadb.Client, collection_name: str, text: str, metadata: dict = None, doc_id: str = None):
    """
    Adds text and its embedding to the specified ChromaDB collection.
    Generates a unique ID if doc_id is not provided.
    The collection must already exist and be configured with an embedding function.
    """
    collection = client.get_collection(name=collection_name) # Assumes collection exists
    
    if doc_id is None:
        doc_id = str(uuid.uuid4())
    
    # ChromaDB automatically handles embedding if an embedding function is set for the collection.
    # We just provide the document.
    collection.add(
        documents=[text],
        metadatas=[metadata] if metadata else [{}], # Ensure metadata is a list of dicts
        ids=[doc_id]
    )
    #print(f"Added document ID {doc_id} to collection '{collection_name}'.") # For debugging

def query_collection(client: chromadb.Client, collection_name: str, query_text: str, n_results: int = 3):
    """
    Queries the collection with query_text, gets embeddings, 
    and returns n_results most relevant documents.
    The collection must already exist and be configured with an embedding function.
    """
    collection = client.get_collection(name=collection_name) # Assumes collection exists
    
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    #print(f"Query results from '{collection_name}': {results['documents']}") # For debugging
    return results['documents'][0] if results['documents'] else []

if __name__ == '__main__':
    # Example Usage (for testing this module directly)
    print("Testing vector_utils.py...")
    
    # Initialize DB and get client
    test_client = init_db(path="./test_chroma_db", collection_name="test_collection")
    print(f"Test DB client: {test_client}")

    # Add some documents
    add_text_to_collection(test_client, "test_collection", "This is a test document about apples.", {"source": "test"}, "doc1")
    add_text_to_collection(test_client, "test_collection", "Another test document, this one about bananas.", {"source": "test"}, "doc2")
    add_text_to_collection(test_client, "test_collection", "Oranges are a citrus fruit.", {"source": "test"}, "doc3")

    print("Finished adding documents.")

    # Query the collection
    query = "Tell me about fruits"
    retrieved_docs = query_collection(test_client, "test_collection", query, n_results=2)
    print(f"Query: '{query}'")
    print("Retrieved documents:")
    for doc in retrieved_docs:
        print(f"- {doc}")

    # Clean up the test database directory
    import shutil
    try:
        shutil.rmtree("./test_chroma_db")
        print("Cleaned up test_chroma_db directory.")
    except OSError as e:
        print(f"Error cleaning up test_chroma_db: {e}")
