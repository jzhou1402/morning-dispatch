import httpx
from datetime import date

def fetch(count=3):
    today = date.today()
    url = (
        f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events"
        f"/{today.month}/{today.day}"
    )
    resp = httpx.get(url, headers={"User-Agent": "MorningDispatch/1.0 (personal)"}, timeout=10)
    events = resp.json().get("events", [])[:count]
    return [{"year": e["year"], "text": e["text"]} for e in events]
