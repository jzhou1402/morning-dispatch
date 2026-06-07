import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

FEEDS = [
    ("TechCrunch NYC",  "https://techcrunch.com/tag/new-york/feed/"),
    ("Built In NYC",    "https://www.builtinnyc.com/rss.xml"),
    ("AlleyWatch",      "https://www.alleywatch.com/feed"),
]

def _parse_feed(name: str, url: str, count: int = 2) -> list:
    req = urllib.request.Request(url, headers={"User-Agent": "MorningDispatch/1.0"})
    with urllib.request.urlopen(req, timeout=12) as r:
        root = ET.fromstring(r.read())

    items = root.findall(".//item")[:count]
    results = []
    for item in items:
        title = (item.findtext("title") or "").strip()
        link  = (item.findtext("link")  or "").strip()
        desc  = (item.findtext("description") or "").strip()
        # strip HTML tags from description
        import re
        desc = re.sub(r"<[^>]+>", "", desc)[:160].strip()
        results.append({"source": name, "title": title, "url": link, "summary": desc})
    return results

def fetch(count=2) -> list:
    articles = []
    for name, url in FEEDS:
        try:
            articles.extend(_parse_feed(name, url, count))
        except Exception:
            continue
    return articles or None
