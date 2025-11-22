import os.path
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --- Configuration ---
# We are asking to SEND emails, not read them.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS_FILE = "credentials.json" # We re-use the same file
TOKEN_FILE = "token_gmail.json"       # We create a NEW token file

def get_gmail_service():
    """Handles Gmail authentication and returns a service object."""
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
                return get_gmail_service()
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print("Error: credentials.json file not found.")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            # This will open a browser for you to log in
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        return service
    except Exception as e:
        print(f"Error building Gmail service: {e}")
        return None

# --- Our Python Function ---

def send_email_report(to_address: str, subject: str, body: str, attachment_path: str = None) -> str:
    """
    Creates and sends an email.

    Args:
        to_address: The recipient's email address.
        subject: The subject line of the email.
        body: The plain text body of the email.
        attachment_path: (Optional) Path to a file to attach.

    Returns:
        A success or error message.
    """
    service = get_gmail_service()
    if not service:
        return "Error: Could not authenticate with Gmail."

    try:
        # Create the email message
        message = MIMEMultipart()
        message["to"] = to_address
        message["subject"] = subject

        # Add the email body
        message.attach(MIMEText(body, "plain"))

        # Add the attachment (if one is provided)
        if attachment_path and os.path.exists(attachment_path):
            filename = os.path.basename(attachment_path)
            with open(attachment_path, "rb") as attachment_file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment_file.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={filename}",
            )
            message.attach(part)

        # Encode the entire message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {"raw": raw_message}

        # Send the email
        # 'me' is a special ID that means the authenticated user
        sent_message = (
            service.users().messages().send(userId="me", body=body).execute()
        )
        return f"Success! Message sent to {to_address}. Message ID: {sent_message['id']}"

    except Exception as e:
        return f"An error occurred while sending email: {e}"
