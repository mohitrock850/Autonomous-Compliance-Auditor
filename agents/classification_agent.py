import json
import os
import regex as re
from google.adk.sessions import Session
from models import generate_text

# Import standard tools
from tools.google_drive_tool import read_google_drive_file
from tools.file_reader_tool import read_document_content
from tools.web_scraper_tool import scrape_website_text

# --- NEW IMPORT: VISION TOOL ---
from tools.vision_tool import analyze_image_document

class ClassificationAgent:
    """
    Agent 2 (REVISED): Batch processes all jobs.
    Now supports IMAGES (OCR) using the Vision Tool.
    """
    
    def __init__(self):
        # We use double brackets {{ }} to escape JSON examples in the prompt
        self.prompt_template = """
        You are a document classification expert. Analyze the provided text
        and classify it into one of these categories:
        - Contract / Agreement
        - Internal Policy / Procedure
        - Audit Report / Financial Statement
        - Regulatory Text
        - Other / Unknown

        Provide your answer as a JSON object with a single key "doc_type".
        Your response MUST contain ONLY the JSON object and no other text.
        Example: {{ "doc_type": "Contract / Agreement" }}
        ---
        DOCUMENT TEXT (first 2000 chars):
        {document_text}
        """

    def _extract_json(self, text: str) -> dict | None:
        print(f"[JSON Extractor] Cleaning raw response: {text[:100]}...") 
        try:
            json_start = text.find('{')
            json_end = text.rfind('}')
            
            if json_start == -1 or json_end == -1:
                print("[JSON Extractor] No JSON object found in response.")
                return None
                
            json_str = text[json_start:json_end+1]
            return json.loads(json_str)
            
        except Exception as e:
            print(f"[JSON Extractor] Parsing failed: {e}")
            return None

    def run(self, session: Session) -> Session:
        print("--- 🧐 Agent 2: Classification Agent Running (with Vision) ---")
        
        try:
            queue = session.state.get("processing_queue")
            if not queue:
                raise Exception("No 'processing_queue' found in session. Agent 1 may have failed.")
            
            print(f"Found {len(queue)} jobs to classify.")
            classified_jobs = [] 

            for job in queue:
                print(f"--- Processing job: {job['file_name']} ---")
                try:
                    content = ""
                    local_filepath = None
                    
                    # --- 1. DOWNLOAD / ACCESS ---
                    if job["source_type"] == "drive":
                        print(f"Downloading file from Drive: {job['file_name']}")
                        download_status = read_google_drive_file(job["file_id"])
                        if "Successfully downloaded" not in download_status:
                            raise Exception(f"Failed to download file: {download_status}")
                        local_filepath = f"./{job['file_name']}"
                        
                        # --- 2. READ CONTENT (TEXT vs IMAGE) ---
                        file_ext = os.path.splitext(job['file_name'])[1].lower()
                        
                        if file_ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
                            print(f"📸 Image detected ({file_ext}). Using Vision Tool...")
                            content = analyze_image_document(local_filepath)
                        else:
                            print(f"📄 Text document detected ({file_ext}). Using File Reader...")
                            content = read_document_content(local_filepath)
                    
                    elif job["source_type"] == "url":
                        print(f"Scraping URL: {job['url']}")
                        content = scrape_website_text(job['url'])
                    
                    if "Error:" in (content or "") or not content:
                        raise Exception(f"Failed to read content for {job['file_name']}: {content}")
                    
                    print(f"Read {len(content)} characters. Classifying...")

                    # --- 3. CLASSIFY ---
                    prompt = self.prompt_template.format(document_text=content[:2000])
                    raw_response = generate_text(prompt)
                    
                    print(f"[Gemini] Raw Response: {raw_response}")
                    response_json = self._extract_json(raw_response)
                    
                    if response_json:
                        doc_type = response_json.get("doc_type", "Other / Unknown")
                    else:
                        print("Could not parse JSON, defaulting to 'Other / Unknown'")
                        doc_type = "Other / Unknown"
                    
                    print(f"Classification: {doc_type}")
                    
                    classified_jobs.append({
                        "file_name": job["file_name"],
                        "source_id": job.get("file_id") or job.get("url"),
                        "doc_type": doc_type,
                        "full_content": content 
                    })

                    # Clean up
                    if local_filepath and os.path.exists(local_filepath):
                        os.remove(local_filepath)

                except Exception as e:
                    print(f"Failed to process job {job['file_name']}: {e}")
                    classified_jobs.append({
                        "file_name": job["file_name"],
                        "source_id": job.get("file_id") or job.get("url"),
                        "doc_type": "Failed to Process",
                        "full_content": None,
                        "error": str(e)
                    })
                
            session.state["classified_jobs"] = classified_jobs
            print(f"--- Batch classification complete. {len(classified_jobs)} jobs processed. ---")

        except Exception as e:
            print(f"Classification Agent Error: {e}")
            session.state["error"] = f"Classification Error: {e}"
        
        return session