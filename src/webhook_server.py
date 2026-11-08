import json
import os
from pathlib import Path

from flask import Flask, jsonify, request

from paypal_client import api

app = Flask(__name__)
DATA = Path("data")
DATA.mkdir(exist_ok=True)
EVENT_LOG = DATA / "events.jsonl"
SEEN_IDS = DATA / "seen_event_ids.txt"

REQUIRED_HEADERS = [
    "PAYPAL-AUTH-ALGO",
    "PAYPAL-CERT-URL",
    "PAYPAL-TRANSMISSION-ID",
    "PAYPAL-TRANSMISSION-SIG",
    "PAYPAL-TRANSMISSION-TIME",
]


def seen_ids():
    return set(SEEN_IDS.read_text().split()) if SEEN_IDS.exists() else set()


@app.post("/webhook")
def webhook():
    h = request.headers

    # 0. Reject unsigned requests before any API call
    if any(not h.get(name) for name in REQUIRED_HEADERS):
        return jsonify({"error": "missing PayPal signature headers"}), 400

    try:
        event = request.get_json(force=True)

        # 1. Verify the event came from PayPal
        check = api("POST", "/v1/notifications/verify-webhook-signature", {
            "auth_algo": h.get("PAYPAL-AUTH-ALGO"),
            "cert_url": h.get("PAYPAL-CERT-URL"),
            "transmission_id": h.get("PAYPAL-TRANSMISSION-ID"),
            "transmission_sig": h.get("PAYPAL-TRANSMISSION-SIG"),
            "transmission_time": h.get("PAYPAL-TRANSMISSION-TIME"),
            "webhook_id": os.environ["PAYPAL_WEBHOOK_ID"],
            "webhook_event": event,
        })
    except Exception as exc:
        return jsonify({"error": "verification failed", "detail": str(exc)[:200]}), 400

    if check.get("verification_status") != "SUCCESS":
        return jsonify({"error": "signature not verified"}), 400

    # 2. Ignore events already processed
    event_id = event["id"]
    if event_id in seen_ids():
        return jsonify({"status": "duplicate ignored"}), 200

    # 3. Record the event
    record = {
        "event_id": event_id,
        "event_type": event["event_type"],
        "resource_id": event.get("resource", {}).get("id"),
        "create_time": event.get("create_time"),
    }
    with EVENT_LOG.open("a") as f:
        f.write(json.dumps(record) + "\n")
    with SEEN_IDS.open("a") as f:
        f.write(event_id + "\n")
    print("Received:", record)
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(port=5000)
