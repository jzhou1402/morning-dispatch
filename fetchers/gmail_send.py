import base64
import os
from email.message import EmailMessage
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.metadata",
]
TOKEN_FILE = "token_gmail_send.json"
CREDS_FILE = "google_credentials.json"


def _get_service():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def _default_recipient(service):
    profile = service.users().getProfile(userId="me").execute()
    return profile.get("emailAddress")


def send_dispatch(ctx: dict, subject: str, to_email: str = None):
    if not os.path.exists(CREDS_FILE):
        print("  – Email delivery skipped (google_credentials.json missing)")
        return None

    from fetchers.email_digest import build as build_digest

    service      = _get_service()
    recipient    = to_email or os.getenv("DISPATCH_EMAIL_TO") or _default_recipient(service)
    if not recipient:
        print("  – Email delivery skipped (no recipient)")
        return None

    html = build_digest(ctx)

    message = EmailMessage()
    message["To"]      = recipient
    message["Subject"] = subject
    message.set_content("Open in an HTML-capable email client to view your Morning Dispatch.")
    message.add_alternative(html, subtype="html")

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    result = service.users().messages().send(
        userId="me",
        body={"raw": raw},
    ).execute()

    print(f"  ✓ Email delivered to {recipient}")
    return result
