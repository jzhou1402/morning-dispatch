import os
import json

SYSTEM_PROMPT = """You are a personal assistant filtering a morning email digest.
Given a list of emails, return only the ones that are genuinely worth reading —
things like: messages from real people, important updates, interesting news,
financial alerts, or anything requiring action.

Exclude: marketing emails, newsletters, automated notifications, promotional offers,
subscription digests, social media alerts, or anything that feels like noise.

Return a JSON array of the email indices (0-based) you want to keep, ranked by importance.
Example: [2, 0, 4]
Return ONLY the JSON array, nothing else."""

def filter_emails(emails: list) -> list:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not emails:
        return emails

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
