import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core import exceptions

# Load the .env file
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please check your .env file.")

genai.configure(api_key=API_KEY)

# --- CONFIGURATION ---
# We switch to "gemini-2.5-flash" which is the latest stable Flash model.
# It has higher rate limits than Pro and is available in the v1beta API.
MODEL_NAME = "gemini-2.5-flash" 

generation_config = {
    "temperature": 0.2,
    "top_p": 1.0,
    "top_k": 1,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

llm = genai.GenerativeModel(
    model_name=MODEL_NAME,
    generation_config=generation_config,
    safety_settings=safety_settings
)

print(f"{MODEL_NAME} model initialized successfully.")

# --- SMART HELPER FUNCTION ---
def generate_text(prompt: str) -> str:
    """
    Calls the LLM with automatic retry logic for rate limits (429 errors).
    """
    max_retries = 10
    base_delay = 5
    
    for attempt in range(max_retries):
        try:
            response = llm.generate_content(prompt)
            return response.text
            
        except exceptions.ResourceExhausted:
            # Handle Rate Limits (429 Errors)
            wait_time = base_delay * (1.5 ** attempt) 
            print(f"   (Rate limit hit. Pausing for {int(wait_time)}s...)")
            time.sleep(wait_time)
            
        except Exception as e:
            # Handle Model Not Found (404) specifically to give a useful hint
            if "404" in str(e):
                print(f"\nCRITICAL ERROR: Model '{MODEL_NAME}' not found.")
                print("Try running this script to see available models:")
                print("import google.generativeai as genai; print([m.name for m in genai.list_models()])")
                return "Error: Model not found."
            
            print(f"Error during Gemini generation: {e}")
            return f"Error: {e}"
            
    return "Error: Failed to generate response after multiple retries."