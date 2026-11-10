import os

import requests

MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def explain(risk, failed, action):
    """One plain sentence explaining a decision. Returns None on any failure."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    prompt = (
        "In one plain sentence for a small business owner, explain this retention decision. "
        f"Inputs: churn risk {risk} on a 0 to 1 scale, failed payments {failed}, action {action}. "
        "Say that fixed rules chose the action. Do not invent facts."
    )
    try:
        r = requests.post(
            URL,
            headers={"x-goog-api-key": key, "Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=15,
        )
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return None
