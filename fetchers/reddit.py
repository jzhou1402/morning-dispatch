import httpx
import os
import xml.etree.ElementTree as ET

DEFAULT_SUBREDDITS = ["technology", "science", "worldnews"]

def fetch():
    subreddits = [
        s.strip()
        for s in os.getenv("REDDIT_SUBREDDITS", ",".join(DEFAULT_SUBREDDITS)).split(",")
    ]

    headers = {"User-Agent": "MorningDispatch/1.0 (personal RSS reader)"}
    posts = []

    for sub in subreddits:
        try:
            resp = httpx.get(
                f"https://www.reddit.com/r/{sub}/top/.rss",
                params={"t": "day", "limit": 1},
                headers=headers,
                timeout=10,
                follow_redirects=True,
            )
            root = ET.fromstring(resp.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entry = root.find("atom:entry", ns)
            if entry is None:
                continue
            title = entry.findtext("atom:title", default="", namespaces=ns).strip()
            link  = entry.find("atom:link", ns)
            url   = link.get("href", "") if link is not None else ""
            posts.append({"subreddit": sub, "title": title, "url": url})
        except Exception:
            continue

    return posts or None
