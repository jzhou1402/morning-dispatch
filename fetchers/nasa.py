import httpx
import os

def fetch():
    key = os.getenv("NASA_API_KEY")
    if not key:
        return None
    resp = httpx.get(
        "https://api.nasa.gov/planetary/apod",
        params={"api_key": key},
        timeout=30,
    )
    d = resp.json()
    return {
        "title":       d.get("title", ""),
        "explanation": d.get("explanation", ""),
        "url":         d.get("url", ""),
        "media_type":  d.get("media_type", "image"),
        "date":        d.get("date", ""),
    }
