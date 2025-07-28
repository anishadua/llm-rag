# app/llm.py (CORRECTED CODE)

import google.generativeai as genai
from app.config import GOOGLE_API_KEY

if not GOOGLE_API_KEY:
    raise ValueError("Google API Key is not set. Cannot initialize Gemini model.")

genai.configure(api_key=GOOGLE_API_KEY)
print("INFO: Google Generative AI configured.")

try:
    model_to_use = 'models/gemini-2.5-flash-lite' 
    gemini_model = genai.GenerativeModel(model_to_use)
    print(f"INFO: Google Gemini '{model_to_use}' model loaded successfully.")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to load Google Gemini '{model_to_use}' model. Error: {e}")
    raise

# This module now exports `gemini_model`.