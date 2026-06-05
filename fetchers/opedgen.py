import os

def fetch(context: dict):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    lines = [f"Date: {context.get('date', 'today')}"]
    if context.get("emails"):
        subjects = [e["subject"] for e in context["emails"][:3]]
        lines.append(f"Top emails: {subjects}")
    if context.get("hackernews"):
        titles = [s["title"] for s in context["hackernews"][:3]]
        lines.append(f"HN top stories: {titles}")
    if context.get("reddit"):
        titles = [p["title"] for p in context["reddit"][:2]]
        lines.append(f"Reddit top posts: {titles}")

    prompt = (
        "Write a short newspaper op-ed column (exactly 120 words) for a personal morning newspaper. "
        "Base it on this context from the reader's day:\n\n"
        + "\n".join(lines)
        + "\n\nWrite in the style of a witty, slightly wry columnist. "
        "Give it a punchy one-line headline on the first line, then the column. "
        "Be specific to the context — no generic filler."
    )

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text
