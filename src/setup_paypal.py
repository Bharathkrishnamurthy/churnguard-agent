from paypal_client import api

product = api("POST", "/v1/catalogs/products", {
    "name": "ChurnGuard Demo Subscription",
    "description": "Sandbox subscription used to test ChurnGuard Agent",
    "type": "SERVICE",
    "category": "SOFTWARE",
}, idempotency_key="churnguard-product-v1")
print("PRODUCT_ID=" + product["id"])

plan = api("POST", "/v1/billing/plans", {
    "product_id": product["id"],
    "name": "ChurnGuard Monthly Demo",
    "description": "Monthly sandbox plan with a payment failure threshold",
    "status": "ACTIVE",
    "billing_cycles": [{
        "frequency": {"interval_unit": "MONTH", "interval_count": 1},
        "tenure_type": "REGULAR",
        "sequence": 1,
        "total_cycles": 0,
        "pricing_scheme": {"fixed_price": {"value": "10.00", "currency_code": "USD"}},
    }],
    "payment_preferences": {
        "auto_bill_outstanding": True,
        "setup_fee_failure_action": "CONTINUE",
        "payment_failure_threshold": 2,
    },
}, idempotency_key="churnguard-plan-v1")
print("PLAN_ID=" + plan["id"])
