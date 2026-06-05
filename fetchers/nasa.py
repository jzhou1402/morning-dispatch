import os
import json
import urllib.request

def fetch():
    key = os.getenv("NASA_API_KEY")
    if not key:
        return None

    url = f"https://api.nasa.gov/planetary/apod?api_key={key}"

    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=20) as resp:
                d = json.loads(resp.read())
            return {
                "title":       d.get("title", ""),
                "explanation": d.get("explanation", ""),
                "url":         d.get("url", ""),
                "media_type":  d.get("media_type", "image"),
                "date":        d.get("date", ""),
            }
        except Exception:
            if attempt == 2:
                raise
            continue
