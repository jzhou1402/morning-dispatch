import os
import json

SYSTEM_PROMPT = """You are a personal assistant filtering a morning email digest for one reader.
Return only emails that are genuinely worth reading. Be ruthless about cutting noise.

KEEP:
- Messages from real, specific people (friends, family, colleagues, recruiters)
- Time-sensitive action items (bills due, packages, appointments, deadlines)
- Financial transactions or account changes the user initiated
- Replies to conversations the user is part of

CUT everything else, including but not limited to:
- Automated security alerts (unusual sign-in, password reset, verification codes)
- Marketing, promotions, deals, or newsletters of any kind
- Social media notifications or digests
- Shipping/order confirmations unless highly time-sensitive
- Repeated emails with the same or near-identical subject from the same sender
- Anything from a no-reply address with no clear personal relevance

Return a JSON array of up to 5 indices (0-based) to KEEP, ranked by importance (most important first).
Example: [2, 0, 4]
If nothing is worth keeping, return: []
Return ONLY the JSON array, nothing else."""


def _deduplicate(emails: list) -> list:
    """Drop near-duplicate emails — same sender + same subject stem."""
    seen = set()
    unique = []
    for e in emails:
        # normalise: lowercase, strip Re:/Fwd:, truncate to first 60 chars
        subject_stem = e["subject"].lower().replace("re:", "").replace("fwd:", "").strip()[:60]
        sender = e["from"].lower()
        key = (sender, subject_stem)
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique


def filter_emails(emails: list) -> list:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not emails:
        return emails

    emails = _deduplicate(emails)

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    email_list = "\n".join(
        f"{i}. From: {e['from']} | Subject: {e['subject']} | Preview: {e['snippet'][:120]}"
        for i, e in enumerate(emails)
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": email_list},
        ],
        max_tokens=100,
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()
    indices = json.loads(raw)
    return [emails[i] for i in indices if i < len(emails)]
