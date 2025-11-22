from google.adk.sessions import Session

from tools.google_drive_tool import list_files_in_drive_folder
import os

class IngestionAgent:
    """
    Agent 1 (REVISED): Finds all work to be done.
    It scans sources (Drive/URL) and creates a "processing_queue" (a list of jobs)
    for the next agents to handle.
    """
    
    def run(self, session: Session, input_data: dict) -> Session:
        """
        Runs the ingestion process.
        
        Args:
            session: The ADK session object.
            input_data: A dict containing either "drive_folder_id" or "url".
            
        Returns:
            The updated session.
        """
        print("--- 🕵️ Agent 1: Ingestion Agent Running (Batch Mode) ---")
        
        processing_queue = [] # This is our new "to-do list"
        
        try:
            if "drive_folder_id" in input_data:
                print(f"Checking Google Drive folder: {input_data['drive_folder_id']}")
                file_list_str = list_files_in_drive_folder(input_data["drive_folder_id"])
                print(file_list_str)
                
                if "ID:" in file_list_str:
                    # Loop through all files found, not just the first one
                    for line in file_list_str.split('\n'):
                        if "ID:" in line:
                            file_name = line.split(", ID:")[0].split("Name: ")[1].strip()
                            file_id = line.split("ID: ")[1].strip()
                            
                            # Add a "drive" job to the queue
                            job = {
                                "source_type": "drive",
                                "file_id": file_id,
                                "file_name": file_name
                            }
                            processing_queue.append(job)
                            
            elif "url" in input_data:
                url = input_data["url"]
                print(f"Adding URL to queue: {url}")
                # Add a "url" job to the queue
                job = {
                    "source_type": "url",
                    "url": url,
                    "file_name": url # Use the URL as the name
                }
                processing_queue.append(job)
                
            else:
                raise ValueError("No 'drive_folder_id' or 'url' provided in input_data.")
                
            if not processing_queue:
                raise Exception("Ingestion complete, but no new files or URLs were found.")
                
            # SUCCESS: Save the entire "to-do list" to the session
            session.state["processing_queue"] = processing_queue
            print(f"Ingestion complete. Found {len(processing_queue)} jobs.")

        except Exception as e:
            print(f"Ingestion Agent Error: {e}")
            session.state["error"] = str(e)
        
        return session