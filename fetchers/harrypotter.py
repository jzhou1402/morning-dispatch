import urllib.request
import json
import random
from datetime import date

def fetch():
    with urllib.request.urlopen("https://hp-api.onrender.com/api/characters", timeout=15) as resp:
        characters = json.loads(resp.read())

    # filter to named characters with a house
    named = [c for c in characters if c.get("name") and c.get("house")]
    if not named:
        return None

    # deterministic pick — same character all day, rotates daily
    rng = random.Random(date.today().toordinal())
    c = rng.choice(named)

    return {
        "name":       c["name"],
        "house":      c["house"],
        "patronus":   c.get("patronus", ""),
        "ancestry":   c.get("ancestry", ""),
        "actor":      c.get("actor", ""),
        "alive":      c.get("alive", True),
        "image":      c.get("image", ""),
        "wand":       c.get("wand", {}),
    }
