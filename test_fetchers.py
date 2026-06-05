#!/usr/bin/env python3
"""
Run each fetcher and report what's working vs. waiting for keys.
Usage: python3 test_fetchers.py
"""
import sys, os, json, traceback
from dotenv import load_dotenv
load_dotenv()

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(name, data):
    preview = json.dumps(data, indent=2)[:300]
    print(f"{GREEN}✓ {name}{RESET}")
    for line in preview.splitlines():
        print(f"  {line}")
    print()

def skip(name, reason="missing API key / credentials"):
    print(f"{YELLOW}– {name}{RESET}  ({reason})\n")

def fail(name, err):
    print(f"{RED}✗ {name}{RESET}  {err}\n")

print(f"\n{BOLD}Morning Dispatch — Fetcher Test{RESET}\n{'─'*40}\n")

# ── No-key fetchers ────────────────────────────────────────────────

print(f"{BOLD}[ No key required ]{RESET}\n")

try:
    from fetchers.hackernews import fetch as hn
    data = hn(count=3)
    ok("Hacker News", data)
except Exception as e:
    fail("Hacker News", e)

try:
    from fetchers.trivia import fetch as trivia
    data = trivia(count=2)
    ok("Trivia (Open Trivia DB)", data)
except Exception as e:
    fail("Trivia", e)

try:
    from fetchers.wikipedia import fetch as wiki
    data = wiki(count=2)
    ok("Wikipedia — On This Day", data)
except Exception as e:
    fail("Wikipedia", e)

# ── Key-required fetchers ──────────────────────────────────────────

print(f"{BOLD}[ Requires API key ]{RESET}\n")

try:
    from fetchers.weather import fetch as weather
    data = weather()
    if data: ok("Weather (OpenWeatherMap)", data)
    else:    skip("Weather", "set OPENWEATHERMAP_KEY in .env")
except Exception as e:
    fail("Weather", e)

try:
    from fetchers.nasa import fetch as nasa
    data = nasa()
    if data: ok("NASA APOD", {**data, "explanation": data["explanation"][:120] + "..."})
    else:    skip("NASA APOD", "set NASA_API_KEY in .env  →  api.nasa.gov")
except Exception as e:
    fail("NASA APOD", e)

try:
    from fetchers.wordofday import fetch as wod
    data = wod()
    if data: ok("Word of the Day (Wordnik)", data)
    else:    skip("Word of the Day", "set WORDNIK_API_KEY in .env  →  developer.wordnik.com")
except Exception as e:
    fail("Word of the Day", e)

try:
    from fetchers.reddit import fetch as reddit
    data = reddit()
    if data: ok("Reddit", data)
    else:    skip("Reddit", "set REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET in .env  →  reddit.com/prefs/apps")
except Exception as e:
    fail("Reddit", e)

try:
    from fetchers.spotify import fetch as spotify
    data = spotify()
    if data: ok("Spotify", data)
    else:    skip("Spotify", "set SPOTIFY_CLIENT_ID + SPOTIFY_CLIENT_SECRET in .env  →  developer.spotify.com/dashboard")
except Exception as e:
    fail("Spotify", traceback.format_exc().splitlines()[-1])

try:
    from fetchers.webull_portfolio import fetch as webull
    data = webull()
    if data: ok("Webull", data)
    else:    skip("Webull", "set WEBULL_USERNAME + WEBULL_PASSWORD in .env")
except Exception as e:
    fail("Webull", e)

# ── OAuth / file-based ─────────────────────────────────────────────

print(f"{BOLD}[ Requires OAuth setup ]{RESET}\n")

try:
    from fetchers.gmail_fetch import fetch as gmail
    data = gmail()
    if data: ok("Gmail", data[:2])
    else:    skip("Gmail", "place google_credentials.json in project root  →  console.cloud.google.com")
except Exception as e:
    fail("Gmail", traceback.format_exc().splitlines()[-1])

try:
    from fetchers.gcalendar import fetch as gcal
    data = gcal()
    if data: ok("Google Calendar", data[:2])
    else:    skip("Google Calendar", "same google_credentials.json as Gmail")
except Exception as e:
    fail("Google Calendar", traceback.format_exc().splitlines()[-1])

try:
    from fetchers.opedgen import fetch as oped
    data = oped({"date": "June 3, 2026", "hackernews": [{"title": "Test story"}]})
    if data: ok("Op-Ed (Anthropic)", {"preview": data[:200]})
    else:    skip("Op-Ed", "set ANTHROPIC_API_KEY in .env  →  console.anthropic.com")
except Exception as e:
    fail("Op-Ed", e)

print(f"{'─'*40}\nDone.\n")
