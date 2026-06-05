import urllib.request
import json

def fetch():
    req = urllib.request.Request("https://catfact.ninja/fact", headers={"User-Agent": "MorningDispatch/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        d = json.loads(resp.read())
    return {"fact": d["fact"]}
