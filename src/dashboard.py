import html
import json
from pathlib import Path

from flask import Flask

DECISIONS = Path("data") / "decisions.jsonl"
app = Flask(__name__)


def load_decisions():
    if not DECISIONS.exists():
        return []
    return [json.loads(line) for line in DECISIONS.read_text().splitlines() if line.strip()]


def esc(value):
    return html.escape("" if value is None else str(value))


@app.get("/")
def index():
    rows = load_decisions()
    orders = sum(1 for r in rows if r.get("status") == "order_created")
    errors = sum(1 for r in rows if r.get("status") == "paypal_error")
    logged = sum(1 for r in rows if r.get("status") == "logged_only")

    table_rows = []
    for r in rows:
        button = ""
        if r.get("approve_url"):
            button = f'<a class="btn" href="{esc(r["approve_url"])}" target="_blank" rel="noopener">Open offer</a>'
        table_rows.append(
            "<tr>"
            f"<td>{esc(r.get('time'))}</td>"
            f"<td>{esc(r.get('subscriber'))}</td>"
            f"<td>{esc(r.get('risk_score'))}</td>"
            f"<td>{esc(r.get('failed_payments'))}</td>"
            f"<td><code>{esc(r.get('action'))}</code></td>"
            f"<td>{esc(r.get('reason'))}</td>"
            f"<td>{esc(r.get('status'))}</td>"
            f"<td>{esc(r.get('order_id'))}</td>"
            f"<td>{esc(r.get('offer_amount'))}</td>"
            f"<td>{button}</td>"
            "</tr>"
        )

    body = "".join(table_rows) or '<tr><td colspan="10">No decisions yet. Run python src\\agent.py first.</td></tr>'

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>ChurnGuard Agent</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 24px; color: #222; }}
h1 {{ font-size: 22px; font-weight: 500; margin: 0 0 4px; }}
p.sub {{ color: #555; margin: 0 0 16px; font-size: 14px; }}
.stats {{ display: flex; gap: 12px; margin-bottom: 16px; }}
.stat {{ border: 1px solid #ccc; border-radius: 8px; padding: 10px 14px; font-size: 14px; }}
.stat b {{ font-size: 20px; font-weight: 500; display: block; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
th, td {{ border: 1px solid #ddd; padding: 6px 8px; text-align: left; vertical-align: top; }}
th {{ background: #f3f5f8; font-weight: 500; }}
code {{ background: #f3f5f8; padding: 1px 4px; border-radius: 4px; }}
.btn {{ display: inline-block; padding: 4px 10px; border: 1px solid #185FA5; color: #185FA5; border-radius: 6px; text-decoration: none; }}
.note {{ margin-top: 16px; font-size: 12px; color: #666; }}
</style></head>
<body>
<h1>ChurnGuard Agent: decisions</h1>
<p class="sub">Rule-based decisions from data/decisions.jsonl. Read-only.</p>
<div class="stats">
  <div class="stat"><b>{len(rows)}</b>subscribers</div>
  <div class="stat"><b>{orders}</b>offers created</div>
  <div class="stat"><b>{logged}</b>logged only</div>
  <div class="stat"><b>{errors}</b>PayPal errors</div>
</div>
<table>
<tr><th>Time (UTC)</th><th>Subscriber</th><th>Risk</th><th>Failed payments</th><th>Action</th><th>Reason</th><th>Status</th><th>PayPal order</th><th>Offer (USD)</th><th>Offer</th></tr>
{body}
</table>
<p class="note">Only the sandbox buyer account triggers a PayPal call. Other rows are demo subscribers and are logged only. Offers are unpaid sandbox orders; the approval page is the evidence of the offer.</p>
</body></html>"""


if __name__ == "__main__":
    app.run(port=5001)