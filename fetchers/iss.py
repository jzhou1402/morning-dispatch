import urllib.request
import json

def fetch():
    with urllib.request.urlopen("http://api.open-notify.org/astros.json", timeout=10) as r:
        crew_data = json.loads(r.read())
    with urllib.request.urlopen("http://api.open-notify.org/iss-now.json", timeout=10) as r:
        loc_data = json.loads(r.read())

    crew = [p["name"] for p in crew_data.get("people", []) if p.get("craft") == "ISS"]
    pos  = loc_data.get("iss_position", {})

    return {
        "crew":      crew,
        "crew_count": len(crew),
        "lat":       round(float(pos.get("latitude",  0)), 2),
        "lon":       round(float(pos.get("longitude", 0)), 2),
    }
