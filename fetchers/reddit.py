import httpx
import os

DEFAULT_SUBREDDITS = ["technology", "science", "worldnews"]

def fetch():
    client_id     = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    if not client_id or not client_secret:
        return None

    subreddits = [
        s.strip()
        for s in os.getenv("REDDIT_SUBREDDITS", ",".join(DEFAULT_SUBREDDITS)).split(",")
    ]

    token_resp = httpx.post(
        "https://www.reddit.com/api/v1/access_token",
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        headers={"User-Agent": "MorningDispatch/1.0 (personal)"},
        timeout=10,
    )
    token = token_resp.json()["access_token"]
    headers = {
        "Authorization": f"bearer {token}",
        "User-Agent": "MorningDispatch/1.0 (personal)",
    }

    posts = []
    for sub in subreddits:
        resp = httpx.get(
            f"https://oauth.reddit.com/r/{sub}/top",
            params={"t": "day", "limit": 1},
            headers=headers,
            timeout=10,
        )
        children = resp.json().get("data", {}).get("children", [])
        if children:
            d = children[0]["data"]
            posts.append({
                "subreddit": sub,
                "title":     d["title"],
                "url":       d.get("url", f"https://reddit.com{d['permalink']}"),
                "score":     d["score"],
                "comments":  d["num_comments"],
            })
    return posts
