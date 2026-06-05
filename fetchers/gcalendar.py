import os
from datetime import datetime, timezone

SCOPES     = ["https://www.googleapis.com/auth/calendar.readonly"]
TOKEN_FILE = "token_calendar.json"
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
    return build("calendar", "v3", credentials=creds)

def fetch(max_results=10):
    if not os.path.exists(CREDS_FILE):
        return None

    service  = _get_service()
    now      = datetime.now(timezone.utc)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=0)
    events_result = service.events().list(
        calendarId="primary",
        timeMin=now.isoformat(),
        timeMax=end_of_day.isoformat(),
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = []
    for e in events_result.get("items", []):
        start_raw = e["start"].get("dateTime", e["start"].get("date", ""))
        try:
            from datetime import datetime as dt
            start_fmt = dt.fromisoformat(start_raw).strftime("%-I:%M %p")
        except Exception:
            start_fmt = start_raw
        events.append({
            "title":    e.get("summary", "(no title)"),
            "start":    start_fmt,
            "location": e.get("location", ""),
            "attendees": len(e.get("attendees", [])),
        })
    return events
