import csv
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from paypal_client import api

DATA = Path("data")
DATA.mkdir(exist_ok=True)
SCORED = DATA / "scored_subscribers.csv"
DECISIONS = DATA / "decisions.jsonl"

BUYER = os.environ.get("SANDBOX_BUYER_EMAIL", "")
OFFER_DISCOUNT = 0.20
DRY_RUN = "--dry-run" in sys.argv


def decide(risk, failed):
    """Fixed rules. Returns (action, reason)."""
    if risk >= 0.7 and failed >= 2:
        return "send_offer_link", "High risk with repeated failed payments: send a discounted payment link"
    if risk >= 0.7:
        return "request_card_update", "High risk without failed payments: ask the subscriber to check their card"
    if risk >= 0.5:
        return "offer_discount", "Medium risk: offer a retention discount"
    return "no_action", "Low risk: no action needed"


def act(email, action, amount):
    if action != "send_offer_link":
        return {"status": "logged_only"}
    if email != BUYER:
        return {"status": "logged_only", "note": "not a sandbox account, no PayPal call made"}
    if DRY_RUN:
        return {"status": "logged_only", "note": "dry run, no PayPal call made"}

    offer = f"{float(amount) * (1 - OFFER_DISCOUNT):.2f}"
    order = api("POST", "/v2/checkout/orders", {
        "intent": "CAPTURE",
        "purchase_units": [{
            "reference_id": f"churnguard-{uuid.uuid4()}",
            "description": "ChurnGuard retention offer (20% off)",
            "amount": {"currency_code": "USD", "value": offer},
        }],
        "payment_source": {
            "paypal": {
                "experience_context": {
                    "user_action": "PAY_NOW",
                    "return_url": "https://example.com/return",
                    "cancel_url": "https://example.com/cancel",
                }
            }
        },
    }, idempotency_key=str(uuid.uuid4()))

    approve_url = next(
        link["href"] for link in order["links"] if link["rel"] in ("payer-action", "approve")
    )
    return {"status": "order_created", "order_id": order["id"], "offer_amount": offer, "approve_url": approve_url}


def log(record):
    with DECISIONS.open("a") as f:
        f.write(json.dumps(record) + "\n")


def main():
    if not SCORED.exists():
        raise SystemExit("Run python src\\score_subscribers.py first.")
    with SCORED.open() as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        risk = float(row["risk_score"])
        failed = int(row["failed_payments"])
        action, reason = decide(risk, failed)

        try:
            result = act(row["email"], action, row["outstanding_amount"])
        except RuntimeError as exc:
            result = {"status": "paypal_error", "detail": str(exc)[:300]}

        record = {
            "time": datetime.now(timezone.utc).isoformat(),
            "subscriber": row["email"],
            "risk_score": risk,
            "score_source": "churn_model.joblib",
            "failed_payments": failed,
            "action": action,
            "reason": reason,
            **result,
        }
        log(record)
        print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
