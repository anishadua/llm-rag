# app/config.py

import os
from dotenv import load_dotenv

load_dotenv()

# --- Directory Paths ---
UPLOAD_DIR = "uploaded_documents"
VECTOR_DB_DIR = "chroma_db"

# --- Document Limits ---
MAX_DOCUMENTS_LIMIT = 20
MAX_PAGES_PER_DOCUMENT = 1000

# --- MongoDB Configuration ---
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "ragsystem_db") 
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "document_metadata") 

# Ensure MongoDB URI is provided
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable not set. Please add it to your .env file.")

# --- Google Gemini API Key ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Ensure Google API key is provided
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set. Please add it to your .env file.")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

print("Configuration loaded successfully.")