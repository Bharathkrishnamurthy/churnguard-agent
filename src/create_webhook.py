import os

from paypal_client import api

EVENTS = [
    "BILLING.SUBSCRIPTION.ACTIVATED",
    "BILLING.SUBSCRIPTION.PAYMENT.FAILED",
    "BILLING.SUBSCRIPTION.SUSPENDED",
    "BILLING.SUBSCRIPTION.CANCELLED",
]
hook = api("POST", "/v1/notifications/webhooks", {
    "url": os.environ["WEBHOOK_URL"],
    "event_types": [{"name": e} for e in EVENTS],
})
print("PAYPAL_WEBHOOK_ID=" + hook["id"])
