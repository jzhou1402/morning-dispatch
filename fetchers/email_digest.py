"""
Full Morning Dispatch email — all sections, table-based, inline styles.
Renders correctly in Gmail, Apple Mail, Outlook.
"""

ACCENT = "#7a1a1a"
INK    = "#1a1208"
LIGHT  = "#5a4a30"
PAPER  = "#f5f0e8"
DARK   = "#ece5d4"
BORDER = "#c8b89a"
GREEN  = "#1a5c1a"
FONT   = "Georgia,'Times New Roman',serif"


def _section(title: str, body: str) -> str:
    return f"""
  <tr><td style="padding:0 28px;">
    <div style="border-bottom:1px solid {BORDER};margin:18px 0 10px;
                font-size:10px;font-weight:bold;letter-spacing:0.18em;
                text-transform:uppercase;color:{ACCENT};font-family:{FONT};
                padding-bottom:4px;">{title}</div>
    {body}
  </td></tr>"""


def _divider() -> str:
    return f'<tr><td style="padding:0 28px;"><hr style="border:none;border-top:1px solid {BORDER};margin:4px 0;"/></td></tr>'


def build(ctx: dict, dispatch_url: str = "") -> str:
    sleep      = ctx.get("sleep", {})
    weather    = ctx.get("weather")
    emails     = ctx.get("emails") or []
    hackernews = ctx.get("hackernews") or []
    calendar   = ctx.get("calendar") or []
    portfolio  = ctx.get("portfolio") or []
    reddit     = ctx.get("reddit") or []
    spotify    = ctx.get("spotify")
    trivia     = ctx.get("trivia") or []
    catfact    = ctx.get("catfact")
    rm         = ctx.get("rickandmorty")
    iss        = ctx.get("iss")
    spaceflight = ctx.get("spaceflight") or []
    apod       = ctx.get("apod")
    on_this_day = ctx.get("on_this_day") or []
    oped       = ctx.get("oped")

    date_str  = ctx.get("date", "")
    issue_num = ctx.get("issue", "")

    parts = [f"""
<table width="100%" cellpadding="0" cellspacing="0"
       style="background:{PAPER};max-width:620px;margin:0 auto;
              border:1px solid {BORDER};font-family:{FONT};">

  <!-- masthead -->
  <tr><td style="padding:24px 28px 12px;border-bottom:3px double {INK};text-align:center;">
    <div style="font-size:40px;font-family:{FONT};color:{INK};font-weight:bold;letter-spacing:-0.5px;">
      The Morning Dispatch
    </div>
    <div style="font-size:11px;color:{LIGHT};margin-top:4px;font-style:italic;">
      Personal Edition &nbsp;·&nbsp; Curated nightly, delivered at dawn
    </div>
  </td></tr>

  <!-- dateline -->
  <tr><td style="background:{DARK};padding:5px 28px;border-bottom:1px solid {BORDER};">
    <table width="100%" cellpadding="0" cellspacing="0"><tr>
      <td style="font-size:11px;letter-spacing:0.08em;text-transform:uppercase;color:{LIGHT};">No. {issue_num}</td>
      <td style="font-size:11px;letter-spacing:0.08em;text-transform:uppercase;color:{LIGHT};text-align:right;">{date_str}</td>
    </tr></table>
  </td></tr>
"""]

    # ── sleep + weather ────────────────────────────────────────────────
    cells = ""
    if sleep.get("bedtime", "–") != "–":
        for label, val in [("Bedtime", sleep.get("bedtime","–")),
                           ("Wake", sleep.get("wake_time","–")),
                           ("Duration", sleep.get("duration","–")),
                           ("Quality", sleep.get("quality", 0))]:
            cells += f"""<td style="padding:10px 14px;text-align:center;border-right:1px solid {BORDER};">
              <div style="font-size:17px;font-weight:bold;color:{INK};font-family:{FONT};">{val}</div>
              <div style="font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:{LIGHT};">{label}</div>
            </td>"""
    if weather:
        cells += f"""<td style="padding:10px 14px;text-align:center;">
          <div style="font-size:17px;font-weight:bold;color:{INK};font-family:{FONT};">{weather["temp"]}°F</div>
          <div style="font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:{LIGHT};">{weather["city"]}</div>
          <div style="font-size:10px;color:{LIGHT};font-style:italic;">{weather["description"]}</div>
        </td>"""
    if cells:
        parts.append(f"""
  <tr><td style="background:{DARK};border-bottom:2px solid {INK};">
    <table cellpadding="0" cellspacing="0" width="100%"><tr>{cells}</tr></table>
  </td></tr>""")

    # ── letters to the editor ─────────────────────────────────────────
    if emails:
        body = ""
        for e in emails[:5]:
            body += f"""
      <div style="margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid {BORDER};">
        <div style="font-size:14px;font-weight:bold;color:{INK};font-family:{FONT};">{e.get("subject","")}</div>
        <div style="font-size:11px;color:{LIGHT};margin:2px 0;">{e.get("from","")}</div>
        <div style="font-size:12px;color:{INK};font-style:italic;">{e.get("snippet","")[:160]}…</div>
      </div>"""
        parts.append(_section("Letters to the Editor", body))

    # ── markets ───────────────────────────────────────────────────────
    if portfolio:
        tbl = f"""<table cellpadding="5" cellspacing="0" width="100%">
          <tr style="font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:{LIGHT};border-bottom:1px solid {BORDER};">
            <td>Ticker</td><td>Price</td><td>Change</td>
          </tr>"""
        for p in portfolio:
            color = GREEN if p["change"] >= 0 else ACCENT
            sign  = "+" if p["change"] >= 0 else ""
            tbl  += f"""<tr style="border-bottom:1px solid {BORDER};">
            <td style="font-weight:bold;color:{INK};font-size:13px;">{p["ticker"]}</td>
            <td style="color:{INK};font-size:13px;">${p["price"]}</td>
            <td style="color:{color};font-size:13px;">{sign}{p["change"]} ({sign}{p["change_pct"]}%)</td>
          </tr>"""
        tbl += "</table>"
        parts.append(_section("Financial Desk — Markets", tbl))

    # ── schedule ──────────────────────────────────────────────────────
    if calendar:
        body = ""
        for e in calendar[:6]:
            body += f"""<div style="margin-bottom:8px;">
          <span style="font-size:11px;color:{ACCENT};letter-spacing:0.08em;text-transform:uppercase;">{e.get("start","")}</span>
          <span style="font-size:13px;color:{INK};font-weight:bold;margin-left:8px;">{e.get("title","")}</span>
          {"<div style='font-size:11px;color:"+LIGHT+";font-style:italic;'>"+e.get("location","")+"</div>" if e.get("location") else ""}
        </div>"""
        parts.append(_section("Classifieds — Today's Schedule", body))

    # ── hacker news ───────────────────────────────────────────────────
    if hackernews:
        body = ""
        for i, s in enumerate(hackernews, 1):
            body += f"""<div style="margin-bottom:10px;">
          <span style="font-size:11px;color:{LIGHT};">{i}. </span>
          <a href="{s["url"]}" style="font-size:13px;color:{INK};font-weight:bold;text-decoration:none;">{s["title"]}</a>
          <div style="font-size:11px;color:{LIGHT};">{s["score"]} pts · {s["comments"]} comments · by {s["by"]}</div>
        </div>"""
        parts.append(_section("Hacker News", body))

    # ── reddit ────────────────────────────────────────────────────────
    if reddit:
        body = ""
        for p in reddit:
            body += f"""<div style="margin-bottom:10px;">
          <div style="font-size:10px;color:{ACCENT};letter-spacing:0.08em;text-transform:uppercase;">r/{p["subreddit"]}</div>
          <a href="{p["url"]}" style="font-size:13px;color:{INK};font-weight:bold;text-decoration:none;">{p["title"]}</a>
        </div>"""
        parts.append(_section("Reddit", body))

    # ── spotify ───────────────────────────────────────────────────────
    if spotify:
        tracks = "".join(f'<div style="font-size:12px;color:{LIGHT};margin:2px 0;">♪ {t}</div>'
                         for t in spotify.get("recent_tracks", []))
        body = f"""
      <div style="font-size:16px;font-weight:bold;color:{INK};">{spotify.get("top_track","")}</div>
      <div style="font-size:12px;color:{LIGHT};font-style:italic;margin-bottom:8px;">by {spotify.get("top_artist","")}</div>
      {tracks}
      <div style="font-size:11px;color:{LIGHT};margin-top:6px;letter-spacing:0.08em;text-transform:uppercase;">
        {spotify.get("total_played",0)} tracks played recently
      </div>"""
        parts.append(_section("Spotify Recap", body))

    # ── spaceflight news ──────────────────────────────────────────────
    if spaceflight:
        body = ""
        for a in spaceflight:
            body += f"""<div style="margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid {BORDER};">
          <div style="font-size:10px;color:{ACCENT};letter-spacing:0.08em;text-transform:uppercase;">{a["source"]}</div>
          <a href="{a["url"]}" style="font-size:13px;color:{INK};font-weight:bold;text-decoration:none;">{a["title"]}</a>
        </div>"""
        parts.append(_section("Spaceflight News", body))

    # ── trivia ────────────────────────────────────────────────────────
    if trivia:
        body = ""
        for q in trivia:
            body += f"""<div style="margin-bottom:12px;">
          <div style="font-size:10px;color:{ACCENT};letter-spacing:0.08em;text-transform:uppercase;margin-bottom:2px;">
            {q["category"]} · {q["difficulty"]}
          </div>
          <div style="font-size:13px;font-weight:bold;color:{INK};margin-bottom:3px;">{q["question"]}</div>
          <div style="font-size:12px;color:{LIGHT};font-style:italic;">Answer: {q["correct_answer"]}</div>
        </div>"""
        parts.append(_section("Daily Trivia", body))

    # ── on this day ───────────────────────────────────────────────────
    if on_this_day:
        body = ""
        for e in on_this_day:
            body += f"""<div style="margin-bottom:8px;font-size:13px;color:{INK};">
          <span style="font-weight:bold;color:{ACCENT};">{e["year"]}</span> — {e["text"]}
        </div>"""
        parts.append(_section("On This Day in History", body))

    # ── cat fact ──────────────────────────────────────────────────────
    if catfact:
        body = f'<div style="font-size:13px;color:{INK};font-style:italic;line-height:1.6;">{catfact["fact"]}</div>'
        parts.append(_section("Cat Fact of the Day", body))

    # ── rick & morty ──────────────────────────────────────────────────
    if rm:
        status_color = GREEN if rm["status"] == "Alive" else (ACCENT if rm["status"] == "Dead" else LIGHT)
        img = f'<img src="{rm["image"]}" width="120" style="display:block;margin-bottom:8px;" alt="{rm["name"]}"/>' if rm.get("image") else ""
        body = f"""{img}
      <div style="font-size:15px;font-weight:bold;color:{INK};">{rm["name"]}</div>
      <div style="font-size:12px;color:{LIGHT};margin-top:3px;">
        {rm["species"]} · {rm["gender"]} · <span style="color:{status_color};">{rm["status"]}</span>
      </div>
      <div style="font-size:12px;color:{LIGHT};">From: {rm["origin"]}</div>
      <div style="font-size:12px;color:{LIGHT};">Last seen: {rm["location"]}</div>"""
        parts.append(_section("Rick &amp; Morty — Character of the Day", body))

    # ── ISS ───────────────────────────────────────────────────────────
    if iss:
        crew = " · ".join(iss["crew"])
        body = f"""
      <div style="font-size:28px;font-weight:bold;color:{INK};line-height:1;">{iss["crew_count"]}</div>
      <div style="font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:{LIGHT};margin-bottom:8px;">Crew Members Aboard</div>
      <div style="font-size:12px;color:{INK};line-height:1.6;">{crew}</div>
      <div style="font-size:11px;color:{LIGHT};margin-top:6px;">{iss["lat"]}° lat · {iss["lon"]}° lon</div>"""
        parts.append(_section("International Space Station", body))

    # ── NASA APOD ─────────────────────────────────────────────────────
    if apod:
        img = f'<img src="{apod["url"]}" width="100%" style="display:block;margin-bottom:10px;max-width:560px;" alt="{apod["title"]}"/>' if apod.get("media_type") == "image" else ""
        body = f"""{img}
      <div style="font-size:16px;font-weight:bold;color:{INK};margin-bottom:4px;">{apod["title"]}</div>
      <div style="font-size:10px;color:{LIGHT};letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;">NASA · {apod["date"]}</div>
      <div style="font-size:13px;color:{INK};line-height:1.7;">{apod["explanation"]}</div>"""
        parts.append(_section("NASA — Astronomy Picture of the Day", body))

    # ── op-ed ─────────────────────────────────────────────────────────
    if oped:
        lines = oped.split("\n")
        headline = lines[0] if lines else ""
        text = "".join(f'<p style="margin:0 0 10px;">{l}</p>' for l in lines[1:] if l.strip())
        body = f"""
      <div style="font-size:18px;font-weight:bold;color:{INK};margin-bottom:6px;line-height:1.2;">{headline}</div>
      <div style="font-size:10px;color:{LIGHT};letter-spacing:0.1em;text-transform:uppercase;margin-bottom:10px;border-bottom:1px solid {BORDER};padding-bottom:6px;">By Claude Sonnet · AI Correspondent</div>
      <div style="font-size:13px;color:{INK};line-height:1.75;">{text}</div>"""
        parts.append(_section("The Op-Ed", body))

    # ── footer ────────────────────────────────────────────────────────
    parts.append(f"""
  <tr><td style="padding:16px 28px;border-top:3px double {INK};text-align:center;">
    <div style="font-size:10px;color:{LIGHT};letter-spacing:0.08em;text-transform:uppercase;font-family:{FONT};">
      The Morning Dispatch &nbsp;·&nbsp; Personal Edition
    </div>
  </td></tr>

</table>""")

    return "\n".join(parts)
