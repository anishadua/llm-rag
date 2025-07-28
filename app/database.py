# app/database.py

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME

# --- MongoDB Client Initialization ---
try:
    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client[MONGO_DB_NAME]
    metadata_collection = mongo_db[MONGO_COLLECTION_NAME]
    
    metadata_collection.create_index("filename", unique=True)
    
    print(f"INFO: Successfully connected to MongoDB. Database: '{MONGO_DB_NAME}', Collection: '{MONGO_COLLECTION_NAME}'")
except PyMongoError as e:
    print(f"CRITICAL ERROR: Failed to connect to MongoDB at '{MONGO_URI}'. Please check your MongoDB server and MONGO_URI in .env. Error: {e}")
    raise
except Exception as e:
    print(f"CRITICAL ERROR: An unexpected error occurred during MongoDB initialization: {e}")
    raise

def close_mongo_connection():
    if mongo_client:
        mongo_client.close()
        print("INFO: MongoDB connection closed.")
