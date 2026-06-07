#!/usr/bin/env python3
"""
Morning Dispatch generator.
Usage:  python3 generate.py            # prompts for sleep if not cached
        python3 generate.py --no-open  # skip browser open
        python3 generate.py --no-cache # force re-fetch all data
        python3 generate.py --no-email # skip Gmail delivery
"""
import sys
import os
import json
import argparse
import threading
import webbrowser
import time
from datetime import datetime, date, timedelta
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

load_dotenv()

ROOT        = Path(__file__).parent
SLEEP_CACHE = ROOT / "sleep_cache.json"
SLEEP_HISTORY = ROOT / "sleep_history.json"
FETCH_CACHE = ROOT / "fetch_cache.json"
REPORT      = ROOT / "report.html"

# ── helpers ────────────────────────────────────────────────────────

def _parse_time(s: str):
    s = s.strip().upper()
    for fmt in ("%I:%M %p", "%I:%M%p", "%I %p", "%H:%M"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None

def _duration_str(bedtime: datetime, wake: datetime) -> str:
    if bedtime.hour >= 12:
        wake += timedelta(days=1)
    delta = wake - bedtime
    total = int(delta.total_seconds())
    h, m  = divmod(total // 60, 60)
    return f"{h}h {m}m"

def _quality_label(score: int) -> str:
    if score >= 85: return "Excellent — fully restored."
    if score >= 70: return "Good night's sleep."
    if score >= 55: return "Decent rest."
    return "Rough night."

def _safe_fetch(name: str, fn, *args, **kwargs):
    try:
        result = fn(*args, **kwargs)
        if result is None:
            print(f"  – {name} (not configured)")
        else:
            print(f"  ✓ {name}")
        return result
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        return None

# ── sleep cache ────────────────────────────────────────────────────

def load_sleep_cache():
    if not SLEEP_CACHE.exists():
        return None
    try:
        data = json.loads(SLEEP_CACHE.read_text())
        if data.get("date") == date.today().isoformat():
            return data["sleep"]
    except Exception:
        pass
    return None

def save_sleep_cache(sleep: dict):
    SLEEP_CACHE.write_text(json.dumps({"date": date.today().isoformat(), "sleep": sleep}))
    save_sleep_history(date.today(), sleep)

def load_sleep_history() -> dict:
    history = {}
    if not SLEEP_HISTORY.exists():
        data = {}
    else:
        try:
            data = json.loads(SLEEP_HISTORY.read_text())
        except Exception:
            data = {}
    if isinstance(data, dict):
        history.update(data)

    try:
        cached = json.loads(SLEEP_CACHE.read_text())
        cached_date = cached.get("date")
        if cached_date and cached.get("sleep") and cached_date not in history:
            history[cached_date] = cached["sleep"]
    except Exception:
        pass

    return history

def save_sleep_history(day: date, sleep: dict):
    history = load_sleep_history()
    history[day.isoformat()] = sleep
    SLEEP_HISTORY.write_text(json.dumps(history, indent=2))

def weekly_sleep_scores(today: date) -> dict:
    history = load_sleep_history()
    days = []
    scores = []

    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        entry = history.get(day.isoformat())
        quality = None
        if entry:
            try:
                quality = max(0, min(100, int(entry.get("quality", 0))))
            except (TypeError, ValueError):
                quality = None
        if quality is not None:
            scores.append(quality)
        days.append({
            "date": day.isoformat(),
            "label": day.strftime("%a"),
            "short": day.strftime("%-m/%-d"),
            "quality": quality,
            "has_score": quality is not None,
        })

    avg = round(sum(scores) / len(scores)) if scores else None
    return {"days": days, "average": avg, "count": len(scores)}

# ── fetch cache ────────────────────────────────────────────────────

def load_fetch_cache():
    if not FETCH_CACHE.exists():
        return None
    try:
        data = json.loads(FETCH_CACHE.read_text())
        if data.get("_date") == date.today().isoformat():
            data.pop("_date", None)
            return data
    except Exception:
        pass
    return None

def save_fetch_cache(ctx: dict):
    cache = {k: v for k, v in ctx.items() if k != "sleep"}
    cache["_date"] = date.today().isoformat()
    FETCH_CACHE.write_text(json.dumps(cache, default=str))

# ── sleep input ────────────────────────────────────────────────────

def blank_sleep() -> dict:
    return {"bedtime": "–", "wake_time": "–", "duration": "–", "quality": 0, "note": ""}

def collect_sleep() -> dict:
    cached = load_sleep_cache()
    if cached:
        print("  ✓ Sleep (cached)")
        return cached
    return blank_sleep()

# ── build context ──────────────────────────────────────────────────

def build_context(sleep: dict) -> dict:
    cached = load_fetch_cache()
    if cached:
        print("\nUsing cached data (expires midnight) — run with --no-cache to refresh")
        cached["sleep"] = sleep
        return cached

    print("\nFetching data…")

    from fetchers.hackernews       import fetch as hn_fetch
    from fetchers.trivia           import fetch as trivia_fetch
    from fetchers.wikipedia        import fetch as wiki_fetch
    from fetchers.weather          import fetch as weather_fetch
    from fetchers.nasa             import fetch as nasa_fetch
    from fetchers.wordofday        import fetch as wod_fetch
    from fetchers.gmail_fetch      import fetch as gmail_fetch
    from fetchers.gcalendar        import fetch as gcal_fetch
    from fetchers.reddit           import fetch as reddit_fetch
    from fetchers.spotify          import fetch as spotify_fetch
    from fetchers.webull_portfolio import fetch as webull_fetch
    from fetchers.opedgen          import fetch as oped_fetch
    from fetchers.email_filter     import filter_emails
    from fetchers.catfact          import fetch as catfact_fetch
    from fetchers.rickandmorty     import fetch as rm_fetch
    from fetchers.iss              import fetch as iss_fetch
    from fetchers.spaceflight      import fetch as sf_fetch
    from fetchers.nyc_startups     import fetch as nyc_fetch
    from fetchers.plants           import fetch as plants_fetch

    hackernews  = _safe_fetch("Hacker News",  hn_fetch,     count=5)
    trivia      = _safe_fetch("Trivia",        trivia_fetch, count=3)
    on_this_day = _safe_fetch("On This Day",   wiki_fetch,   count=3)
    weather     = _safe_fetch("Weather",       weather_fetch)
    apod        = _safe_fetch("NASA APOD",     nasa_fetch)
    word_of_day = _safe_fetch("Word of Day",   wod_fetch)
    emails_raw  = _safe_fetch("Gmail",         gmail_fetch)
    emails      = _safe_fetch("Gmail filter",  filter_emails, emails_raw) if emails_raw else emails_raw
    calendar    = _safe_fetch("Calendar",      gcal_fetch)
    reddit      = _safe_fetch("Reddit",        reddit_fetch)
    spotify     = _safe_fetch("Spotify",       spotify_fetch)
    portfolio   = _safe_fetch("Markets",       webull_fetch)
    catfact     = _safe_fetch("Cat Fact",      catfact_fetch)
    rickandmorty = _safe_fetch("Rick & Morty", rm_fetch)
    iss          = _safe_fetch("ISS",          iss_fetch)
    spaceflight  = _safe_fetch("Spaceflight",  sf_fetch)
    nyc_startups = _safe_fetch("NYC Startups", nyc_fetch)
    plants       = _safe_fetch("Plants",       plants_fetch)

    today     = date.today()
    issue_num = (today - date(2026, 1, 1)).days + 1
    oped      = _safe_fetch("Op-Ed", oped_fetch, {
        "date":       today.strftime("%B %-d, %Y"),
        "emails":     emails,
        "hackernews": hackernews,
        "reddit":     reddit,
    })

    ctx = {
        "date":         today.strftime("%A, %B %-d, %Y"),
        "date_short":   today.strftime("%B %-d, %Y"),
        "vol":          1,
        "issue":        issue_num,
        "generated_at": datetime.now().strftime("%-I:%M %p"),
        "sleep":        sleep,
        "weather":      weather,
        "on_this_day":  on_this_day or [],
        "trivia":       trivia or [],
        "word_of_day":  word_of_day,
        "apod":         apod,
        "emails":       emails or [],
        "calendar":     calendar,
        "hackernews":   hackernews or [],
        "reddit":       reddit or [],
        "spotify":      spotify,
        "portfolio":    portfolio,
        "oped":         oped,
        "plants":       plants,
        "nyc_startups": nyc_startups,
        "catfact":      catfact,
        "rickandmorty": rickandmorty,
        "iss":          iss,
        "spaceflight":  spaceflight,
    }
    save_fetch_cache(ctx)
    return ctx

def add_dispatch_metadata(ctx: dict) -> dict:
    today = date.today()
    is_sunday = today.weekday() == 6
    ctx.update({
        "is_sunday": is_sunday,
        "dispatch_title": "The Sunday Dispatch" if is_sunday else "The Morning Dispatch",
        "sleep_week": weekly_sleep_scores(today),
    })
    return ctx

# ── render ─────────────────────────────────────────────────────────

def render(ctx: dict) -> str:
    env  = Environment(loader=FileSystemLoader(str(ROOT)), autoescape=True)
    tmpl = env.get_template("template.jinja2")
    return tmpl.render(**ctx)

# ── email delivery ─────────────────────────────────────────────────

def deliver_email(ctx: dict, to_email: str = None):
    from fetchers.gmail_send import send_dispatch

    subject = f"{ctx['dispatch_title']} - {ctx['date_short']}"
    return send_dispatch(ctx, subject, to_email=to_email)

# ── sleep form server ──────────────────────────────────────────────

class _SleepHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)
        try:
            data        = json.loads(body)
            bedtime_raw = data.get("bedtime", "–").strip() or "–"
            wake_raw    = data.get("wake_time", "–").strip() or "–"
            try:
                quality = max(0, min(100, int(data.get("quality", 0))))
            except (ValueError, TypeError):
                quality = 0

            duration = "–"
            if bedtime_raw != "–" and wake_raw != "–":
                bt = _parse_time(bedtime_raw)
                wt = _parse_time(wake_raw)
                if bt and wt:
                    duration = _duration_str(bt, wt)

            sleep = {
                "bedtime":   bedtime_raw,
                "wake_time": wake_raw,
                "duration":  duration,
                "quality":   quality,
                "note":      data.get("note", "").strip() or _quality_label(quality),
            }
            save_sleep_cache(sleep)

            fetch_ctx = load_fetch_cache()
            if fetch_ctx:
                fetch_ctx["sleep"] = sleep
                REPORT.write_text(render(add_dispatch_metadata(fetch_ctx)), encoding="utf-8")

            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(b"ok")
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(str(e).encode())

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, *args):
        pass

def start_sleep_server():
    import socket, signal
    # free the port if a previous run left it open
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("localhost", 5050)) == 0:
            import subprocess
            result = subprocess.run(["lsof", "-ti", ":5050"], capture_output=True, text=True)
            for pid in result.stdout.strip().splitlines():
                try:
                    os.kill(int(pid), signal.SIGTERM)
                except ProcessLookupError:
                    pass
    server = HTTPServer(("localhost", 5050), _SleepHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server

# ── main ───────────────────────────────────────────────────────────

def _upload_dispatch(html: str):
    url    = os.getenv("DISPATCH_URL", "").strip()
    secret = os.getenv("DISPATCH_SECRET", "").strip()
    if not url or not secret:
        return
    try:
        import urllib.request
        req = urllib.request.Request(
            url,
            data=html.encode("utf-8"),
            headers={
                "Authorization": f"Bearer {secret}",
                "Content-Type": "text/html; charset=utf-8",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"  ✓ Uploaded to {url.replace('/dispatch/upload', '/dispatch')}")
    except Exception as e:
        print(f"  ✗ Upload failed: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-open",  action="store_true")
    parser.add_argument("--no-cache", action="store_true", help="Force re-fetch all data")
    parser.add_argument("--no-email", action="store_true", help="Skip Gmail delivery")
    parser.add_argument("--email-to", help="Override DISPATCH_EMAIL_TO for this run")
    args = parser.parse_args()

    if args.no_cache:
        FETCH_CACHE.unlink(missing_ok=True)
        print("Cache cleared — fetching fresh data")

    sleep = collect_sleep()
    ctx   = build_context(sleep)
    ctx   = add_dispatch_metadata(ctx)
    html  = render(ctx)
    REPORT.write_text(html, encoding="utf-8")
    archive_dir = ROOT / "archive"
    archive_dir.mkdir(exist_ok=True)
    archive_file = archive_dir / f"{date.today().isoformat()}.html"
    archive_file.write_text(html, encoding="utf-8")
    print(f"\nWrote {REPORT}")
    print(f"Archived → {archive_file.name}")

    _upload_dispatch(html)

    if not args.no_email:
        try:
            deliver_email(ctx, to_email=args.email_to)
        except Exception as e:
            print(f"  ✗ Email delivery failed: {e}")

    start_sleep_server()

    if not args.no_open:
        webbrowser.open(f"file://{REPORT.resolve()}")

    print("Serving sleep form on :5050  ·  Ctrl+C to quit\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nGoodbye.")

if __name__ == "__main__":
    main()
