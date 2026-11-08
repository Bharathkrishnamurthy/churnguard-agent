from webhook_server import app

client = app.test_client()

# Test 1: unsigned request must be rejected
r = client.post("/webhook", json={"id": "TEST-1", "event_type": "TEST"})
print("unsigned request:", r.status_code, "PASS" if r.status_code == 400 else "FAIL")
