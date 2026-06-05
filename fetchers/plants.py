import os
import urllib.request
import json

PLANTS_URL = os.getenv("PLANTS_URL", "http://localhost:5001/api/plants")


def fetch():
    req = urllib.request.Request(PLANTS_URL, headers={"User-Agent": "MorningDispatch/1.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())
