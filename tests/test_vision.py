import asyncio
from tools.vision_tool import analyze_image_document
import os

def run_test():
    print("--- 👁️ Testing Vision Tool ---")

    image_path = "test_scan.png" 

    if not os.path.exists(image_path):
        print(f"❌ Error: Could not find image '{image_path}'.")
        print("Please run 'create_sample_image.py' first or add your own image.")
        return

    print(f"Sending '{image_path}' to Gemini 1.5 Flash...")

    # Call the tool directly
    result = analyze_image_document(image_path)

    print("\n--- 📝 GEMINI TRANSCRIPTION ---")
    print(result)
    print("-------------------------------")

    if "CONFIDENTIAL CONTRACT" in result or "Payment" in result:
        print("✅ SUCCESS: Text was correctly extracted from the image.")
    else:
        print("⚠️ WARNING: output might be generic or empty. Check the transcription.")

if __name__ == "__main__":
    run_test()