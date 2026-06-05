import urllib.request
import json
import random
from datetime import date

def fetch():
    headers = {"User-Agent": "MorningDispatch/1.0"}

    req = urllib.request.Request("https://rickandmortyapi.com/api/character", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        meta = json.loads(r.read())

    total   = meta["info"]["count"]
    rng     = random.Random(date.today().toordinal())
    char_id = rng.randint(1, total)

    req = urllib.request.Request(f"https://rickandmortyapi.com/api/character/{char_id}", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        c = json.loads(r.read())

    return {
        "name":     c["name"],
        "status":   c["status"],
        "species":  c["species"],
        "gender":   c["gender"],
        "origin":   c["origin"]["name"],
        "location": c["location"]["name"],
        "image":    c["image"],
    }
