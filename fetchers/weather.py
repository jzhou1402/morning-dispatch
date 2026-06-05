import httpx
import os

def fetch():
    key = os.getenv("OPENWEATHERMAP_KEY")
    if not key:
        return None
    city = os.getenv("OPENWEATHERMAP_CITY", "San Francisco")
    resp = httpx.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"q": city, "appid": key, "units": "imperial"},
        timeout=10,
    )
    d = resp.json()
    if d.get("cod") != 200 and "main" not in d:
        return None
    from datetime import datetime
    sunrise = d["sys"]["sunrise"]
    sunset  = d["sys"]["sunset"]
    return {
        "city":        d["name"],
        "temp":        round(d["main"]["temp"]),
        "feels_like":  round(d["main"]["feels_like"]),
        "description": d["weather"][0]["description"].title(),
        "humidity":    d["main"]["humidity"],
        "sunrise":     datetime.fromtimestamp(sunrise).strftime("%-I:%M %p"),
        "sunset":      datetime.fromtimestamp(sunset).strftime("%-I:%M %p"),
    }
