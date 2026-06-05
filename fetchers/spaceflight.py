import urllib.request
import json

def fetch(count=4):
    url = f"https://api.spaceflightnewsapi.net/v4/articles/?limit={count}&ordering=-published_at"
    req = urllib.request.Request(url, headers={"User-Agent": "MorningDispatch/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())

    return [
        {
            "title":    a["title"],
            "url":      a["url"],
            "summary":  a["summary"][:200],
            "source":   a["news_site"],
        }
        for a in data.get("results", [])
    ] or None
