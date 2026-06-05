import httpx
import os

def fetch():
    key = os.getenv("WORDNIK_API_KEY")
    if not key:
        return None
    resp = httpx.get(
        "https://api.wordnik.com/v4/words.json/wordOfTheDay",
        params={"api_key": key},
        timeout=10,
    )
    d = resp.json()
    definitions = d.get("definitions") or []
    examples    = d.get("examples") or []
    return {
        "word":           d.get("word", ""),
        "part_of_speech": definitions[0].get("partOfSpeech", "") if definitions else "",
        "definition":     definitions[0].get("text", "")         if definitions else "",
        "example":        examples[0].get("text", "")            if examples    else "",
    }
