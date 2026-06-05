import os

SCOPES    = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDS_FILE = "google_credentials.json"

TOKEN_FILES = [
    "token_gmail.json",
    "token_gmail_2.json",
]

def _get_service(token_file):
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def _fetch_one(token_file, max_results, query):
    service  = _get_service(token_file)
    results  = service.users().messages().list(userId="me", maxResults=max_results, q=query).execute()
    messages = results.get("messages", [])

    emails = []
    for msg in messages:
        full    = service.users().messages().get(userId="me", id=msg["id"], format="metadata").execute()
        headers = {h["name"]: h["value"] for h in full["payload"]["headers"]}
        emails.append({
            "subject": headers.get("Subject", "(no subject)"),
            "from":    headers.get("From", ""),
            "date":    headers.get("Date", ""),
            "snippet": full.get("snippet", ""),
        })
    return emails

def fetch(max_results=12, query="category:primary newer_than:2d"):
    if not os.path.exists(CREDS_FILE):
        return None

    all_emails = []
    for token_file in TOKEN_FILES:
        try:
            all_emails.extend(_fetch_one(token_file, max_results, query))
        except Exception as e:
            print(f"    [gmail] skipped {token_file}: {e}")

    return all_emails or None
