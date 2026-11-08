import os
import time
from pathlib import Path

import requests

BASE = "https://api-m.sandbox.paypal.com"


def load_env(path=".env"):
    env_file = Path(path)
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


load_env()
_token = {"value": None, "expires_at": 0.0}


def get_token():
    if time.time() < _token["expires_at"] - 60:
        return _token["value"]
    r = requests.post(
        f"{BASE}/v1/oauth2/token",
        auth=(os.environ["PAYPAL_CLIENT_ID"], os.environ["PAYPAL_CLIENT_SECRET"]),
        data={"grant_type": "client_credentials"},
        timeout=30,
    )
    r.raise_for_status()
    body = r.json()
    _token["value"] = body["access_token"]
    _token["expires_at"] = time.time() + body["expires_in"]
    return _token["value"]


def api(method, path, json_body=None, idempotency_key=None):
    headers = {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json",
    }
    if idempotency_key:
        headers["PayPal-Request-Id"] = idempotency_key
    r = requests.request(method, f"{BASE}{path}", headers=headers,
                         json=json_body, timeout=30)
    if not r.ok:
        raise RuntimeError(f"{method} {path} failed: {r.status_code} {r.text}")
    return r.json() if r.text else {}
