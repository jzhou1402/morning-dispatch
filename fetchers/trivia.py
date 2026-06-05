import httpx
import html as html_lib
import random

def fetch(count=3):
    resp = httpx.get(
        "https://opentdb.com/api.php",
        params={"amount": count, "type": "multiple"},
        timeout=10,
    )
    items = resp.json().get("results", [])
    result = []
    for item in items:
        correct = html_lib.unescape(item["correct_answer"])
        incorrect = [html_lib.unescape(a) for a in item["incorrect_answers"]]
        choices = incorrect + [correct]
        random.shuffle(choices)
        result.append({
            "category": html_lib.unescape(item["category"]),
            "difficulty": item["difficulty"],
            "question": html_lib.unescape(item["question"]),
            "correct_answer": correct,
            "choices": choices,
        })
    return result
