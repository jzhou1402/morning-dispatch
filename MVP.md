# Morning Dispatch — MVP

A daily personal newspaper rendered as a local HTML file, opened automatically each morning via `launchd`. All data is fetched by a Python script at generation time and injected into a Jinja2 HTML template.

---

## Sections

### Always-present (no external API)
| Section | Description | Layout placement |
|---|---|---|
| **Masthead** | Newspaper title, date, vol/issue, tagline | Top of page |
| **Sleep Log** | Bedtime, wake time, duration, quality score (manual entry) | Banner below masthead |

---

### Almanac Block
*Grouped into one compact sidebar/banner — weather + daily curiosities.*

| Sub-section | API | Auth |
|---|---|---|
| Weather + sunrise/sunset | OpenWeatherMap API | Free API key |
| Word of the Day | Free Dictionary API or Wordnik | Free |
| On This Day in History | Wikipedia `/api/rest_v1/feed/onthisday` | None |
| Crossword Clue of the Day | NYT crossword (undocumented) | None |
| NASA Photo of the Day | NASA APOD API | Free API key |

---

### Inbox — "Letters to the Editor"
*Each significant email rendered as a formal letter excerpt with sender as byline.*

| Source | API | Auth |
|---|---|---|
| Gmail digest (filtered) | Gmail API v1 | OAuth 2.0 |

---

### Markets — "Financial Desk"
*Formatted as a stock ticker table + brief portfolio narrative.*

| Source | API | Auth |
|---|---|---|
| Webull portfolio + P&L | `webull` PyPI (unofficial) | Webull credentials |

---

### Culture & Discovery
| Section | Description | API | Auth |
|---|---|---|---|
| **Hacker News Top 5** | Top stories of the day | HN Firebase API | None |
| **Reddit Top Posts** | Top posts from chosen subreddits | Reddit API v1 | Free OAuth |
| **Spotify Recap** | What you listened to yesterday, top track | Spotify Web API | OAuth |
| **Trivia** | 3 daily trivia Q&As, categorized | Open Trivia DB (opentdb.com) | None |

---

### Garden Report — "Nature Desk"
*Status of each plant: last watered, next watering due, health note.*

| Source | Description |
|---|---|
| Custom plant web app | Built by us — stores plant name, watering schedule, health logs in a local DB |

---

### Opinion — "The Op-Ed"
*A short AI-generated paragraph commenting on something from the user's week (pulled from email/calendar context).*

| Source | API |
|---|---|
| Claude API (claude-sonnet-4-6) | Anthropic SDK — generates ~150-word op-ed from weekly context |

---

### Schedule — "Classifieds"
*Google Calendar events formatted as classified ads.*

| Source | API | Auth |
|---|---|---|
| Google Calendar | Google Calendar API v3 | OAuth 2.0 |

---

## Newspaper Column Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  MASTHEAD — The Morning Dispatch                                 │
│  dateline · edition bar                                         │
├─────────────────────────────────────────────────────────────────┤
│  SLEEP BANNER — bedtime · wake · duration · quality bar         │
├──────────────────────────────────────┬──────────────────────────┤
│  LETTERS TO THE EDITOR               │  ALMANAC                 │
│  Top email as feature story          │  Weather                 │
│  (drop cap, 2-col body)              │  Word of the Day         │
│                                      │  On This Day             │
│                                      │  Crossword Clue          │
│                                      │  ─────────────────────   │
│                                      │  TRIVIA  (3 Q&As)        │
├──────────────────────────────────────┴──────────────────────────┤
│  MARKETS            │  CLASSIFIEDS         │  GARDEN REPORT      │
│  Webull portfolio   │  Calendar as ads     │  Plant statuses     │
├─────────────────────┴──────────────────────┴────────────────────┤
│  CULTURE & DISCOVERY                                            │
│  HN Top 5  │  Reddit Top 3  │  Spotify Recap  │  NASA APOD      │
├─────────────────────────────────────────────────────────────────┤
│  OP-ED  — AI-generated weekly commentary (~150 words)           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Choice |
|---|---|
| Templating | Jinja2 (Python) |
| Scheduling | macOS `launchd` plist |
| Email | Gmail API v1 + `google-auth` |
| HTTP | `httpx` or `requests` |
| Plant app | FastAPI + SQLite (local) |
| AI (op-ed) | Anthropic SDK (`claude-sonnet-4-6`) |

---

## Build Order

1. **HTML template design** — finalize all sections with fake data ← *current*
2. **Plant web app** — FastAPI + SQLite, simple UI to log plant status
3. **Data pipeline** — one fetcher module per source
4. **Jinja2 wiring** — connect fetchers → template → `report.html`
5. **Sleep log UI** — simple morning input form (or CLI prompt)
6. **launchd scheduling** — auto-generate + open at wake time
7. **Op-ed generation** — Claude API call with weekly context
