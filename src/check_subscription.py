import os
from paypal_client import api

sub_id = os.environ["SUBSCRIPTION_ID"]
sub = api("GET", f"/v1/billing/subscriptions/{sub_id}")
print("STATUS=" + sub["status"])
