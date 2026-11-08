import os
import uuid

from paypal_client import api

sub = api("POST", "/v1/billing/subscriptions", {
    "plan_id": os.environ["PLAN_ID"],
    "subscriber": {
        "name": {"given_name": "Sandbox", "surname": "Buyer"},
        "email_address": os.environ["SANDBOX_BUYER_EMAIL"],
    },
    "application_context": {
        "brand_name": "ChurnGuard Demo",
        "user_action": "SUBSCRIBE_NOW",
        "return_url": "https://example.com/approved",
        "cancel_url": "https://example.com/cancelled",
    },
}, idempotency_key=f"sub-{uuid.uuid4()}")

approve_link = next(link["href"] for link in sub["links"] if link["rel"] == "approve")
print("SUBSCRIPTION_ID=" + sub["id"])
print("APPROVE_URL=" + approve_link)
