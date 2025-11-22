import os
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# Load config
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def analyze_image_document(image_path: str, prompt: str = "Transcribe this document. If it contains a table, output it as Markdown.") -> str:
    """
    Uses Gemini's Vision capabilities to read scanned documents or charts.
    """
    print(f"👁️ Vision Tool: Analyzing {image_path}...")
    
    if not os.path.exists(image_path):
        return f"Error: Image file not found at {image_path}"

    try:
        # UPDATED: Use gemini-2.5-flash as we know 1.5-flash was giving 404s for you
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        img = Image.open(image_path)
        
        # Generate content using the image and prompt
        response = model.generate_content([prompt, img])
        return response.text
        
    except Exception as e:
        print(f"Vision Tool Error: {e}")
        return f"Error analyzing image: {e}"

if __name__ == "__main__":
    print("Vision Tool loaded.")