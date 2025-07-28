# app/vector_store.py

from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import configuration settings
from app.config import VECTOR_DB_DIR

# --- Embedding Model ---
# This model is responsible for converting text into numerical vector representations.

try:
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    print("INFO: SentenceTransformer embeddings model loaded successfully.")
except Exception as e:
    # If the model isn't found, try to trigger a download
    print(f"WARNING: SentenceTransformer model 'all-MiniLM-L6-v2' not found locally. Attempting to download it. Error: {e}")
    from sentence_transformers import SentenceTransformer
    SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    print("INFO: SentenceTransformer embeddings model downloaded and loaded successfully.")


# --- Text Splitter ---
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Maximum number of characters in each chunk
    chunk_overlap=200,      # Number of characters to overlap between consecutive chunks
                            # Overlap helps to preserve context across chunk boundaries.
    length_function=len,    # Function to calculate chunk length (standard for character count)
    is_separator_regex=False, # Use predefined separators (like newlines, spaces)
)
print("INFO: RecursiveCharacterTextSplitter initialized.")


# --- Vector Store (ChromaDB) ---
vectorstore = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)
print(f"INFO: ChromaDB vector store initialized at '{VECTOR_DB_DIR}'.")
