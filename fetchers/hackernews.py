import httpx

BASE = "https://hacker-news.firebaseio.com/v0"

def fetch(count=5):
    ids = httpx.get(f"{BASE}/topstories.json", timeout=10).json()[:count]
    stories = []
    for story_id in ids:
        item = httpx.get(f"{BASE}/item/{story_id}.json", timeout=10).json()
        stories.append({
            "title": item.get("title", ""),
            "url": item.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
            "score": item.get("score", 0),
            "by": item.get("by", ""),
            "comments": item.get("descendants", 0),
        })
    return stories
