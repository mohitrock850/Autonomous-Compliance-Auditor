import os.path
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
# --- (ADK import is removed, we don't need it for this test) ---

# --- Configuration ---
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

# --- Authentication Helper (Runs ONCE) ---
def get_drive_service():
    """Handles Google Drive authentication and returns a service object."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}. Need to re-authenticate.")
                os.remove(TOKEN_FILE) 
                return get_drive_service()
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print("Error: credentials.json file not found.")
                print("Please follow the setup steps to download it.")
                return None
                
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
            
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("drive", "v3", credentials=creds)
        return service
    except Exception as e:
        print(f"Error building Drive service: {e}")
        return None

# --- Our Python Functions (No ADK decorators) ---

def list_files_in_drive_folder(folder_id: str) -> str:
    """
    Lists files in a specified Google Drive folder.
    
    Args:
        folder_id: The ID of the Google Drive folder.
        
    Returns:
        A string listing filenames and their IDs, or an error message.
    """
    service = get_drive_service()
    if not service:
        return "Error: Could not authenticate with Google Drive."
        
    try:
        query = f"'{folder_id}' in parents and trashed=false"
        results = (
            service.files()
            .list(q=query, fields="files(id, name)")
            .execute()
        )
        files = results.get("files", [])

        if not files:
            return "No files found in the specified folder."

        file_list = "Files found:\n"
        for file in files:
            file_list += f"- Name: {file.get('name')}, ID: {file.get('id')}\n"
        return file_list

    except Exception as e:
        return f"An error occurred: {e}"

def read_google_drive_file(file_id: str) -> str:
    """
    Downloads a Google Drive file to the local folder.
    
    Args:
        file_id: The ID of the file to read.
        
    Returns:
        A success or error message.
    """
    service = get_drive_service()
    if not service:
        return "Error: Could not authenticate with Google Drive."

    try:
        request_meta = service.files().get(fileId=file_id, fields="name").execute()
        filename = request_meta.get('name', 'downloaded_file')
        
        request_media = service.files().get_media(fileId=file_id)
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request_media)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")

        # Save the downloaded file to disk
        file_stream.seek(0)
        local_filepath = f"./{filename}" # Saves in the current folder
        with open(local_filepath, 'wb') as f:
            f.write(file_stream.read())

        return f"Successfully downloaded file '{filename}' to {local_filepath}."

    except Exception as e:
        return f"An error occurred while reading file {file_id}: {e}"