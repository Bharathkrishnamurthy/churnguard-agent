import html
import json
import os
from pathlib import Path

from flask import Flask

DECISIONS = Path(os.environ.get("DECISIONS_PATH", "data/decisions.jsonl"))
app = Flask(__name__)

ACTION_STYLE = {
    "send_offer_link": ("badge badge-teal", "Offer sent"),
    "request_card_update": ("badge badge-amber", "Card update"),
    "offer_discount": ("badge badge-blue", "Discount"),
    "no_action": ("badge badge-gray", "No action"),
}

STATUS_STYLE = {
    "order_created": ("pill pill-green", "Order created"),
    "logged_only": ("pill pill-gray", "Logged only"),
    "paypal_error": ("pill pill-red", "PayPal error"),
}

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ChurnGuard Agent</title>
<style>
  :root {
    --bg: #0b1120;
    --card: #131c31;
    --line: #22304d;
    --text: #e6ecf7;
    --muted: #8fa0bf;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    min-height: 100vh;
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
  }
  header {
    padding: 40px 32px 56px;
    background: linear-gradient(120deg, #4338ca 0%, #0f766e 100%);
    box-shadow: 0 10px 30px rgba(0, 0, 0, .35);
  }
  header .eyebrow { font-size: 12px; letter-spacing: .14em; text-transform: uppercase; opacity: .8; }
  header h1 { margin: 6px 0 6px; font-size: 30px; font-weight: 600; }
  header p { margin: 0; opacity: .85; font-size: 14px; }
  main { max-width: 1180px; margin: -30px auto 0; padding: 0 20px 48px; }
  .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 22px; }
  .stat {
    background: var(--card);
    border: 1px solid var(--line);
    border-top: 3px solid var(--accent);
    border-radius: 16px;
    padding: 18px 20px;
  }
  .stat .num { font-size: 30px; font-weight: 600; color: var(--accent); }
  .stat .label { font-size: 13px; color: var(--muted); margin-top: 2px; }
  .panel { background: var(--card); border: 1px solid var(--line); border-radius: 18px; overflow: hidden; }
  .table-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
  th {
    text-align: left;
    font-weight: 600;
    color: var(--muted);
    padding: 14px 16px;
    background: #0f1a2e;
    border-bottom: 1px solid var(--line);
    white-space: nowrap;
  }
  td { padding: 14px 16px; border-bottom: 1px solid var(--line); vertical-align: middle; }
  tr:last-child td { border-bottom: none; }
  tbody tr { transition: background .15s; }
  tbody tr:hover { background: #17233d; }
  .mono { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 12.5px; color: #c7d2ea; }
  .muted { color: var(--muted); }
  .subject { max-width: 230px; word-break: break-all; }
  .reason { max-width: 260px; color: #c7d2ea; line-height: 1.45; }
  .badge, .pill {
    display: inline-block;
    padding: 4px 11px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
    border: 1px solid transparent;
  }
  .badge-teal { background: rgba(20,184,166,.15); color: #5eead4; border-color: rgba(20,184,166,.35); }
  .badge-amber { background: rgba(245,158,11,.14); color: #fcd34d; border-color: rgba(245,158,11,.35); }
  .badge-blue { background: rgba(59,130,246,.15); color: #93c5fd; border-color: rgba(59,130,246,.35); }
  .badge-gray { background: rgba(148,163,184,.12); color: #cbd5e1; border-color: rgba(148,163,184,.3); }
  .pill-green { background: rgba(34,197,94,.14); color: #86efac; }
  .pill-gray { background: rgba(148,163,184,.12); color: #cbd5e1; }
  .pill-red { background: rgba(244,63,94,.14); color: #fda4af; }
  .risk { display: flex; align-items: center; gap: 10px; }
  .risk-bar { width: 70px; height: 6px; border-radius: 6px; background: #22304d; overflow: hidden; }
  .risk-bar span { display: block; height: 100%; background: linear-gradient(90deg, #14b8a6, #818cf8); }
  .btn {
    display: inline-block;
    margin-top: 6px;
    padding: 6px 12px;
    border-radius: 10px;
    background: #6366f1;
    color: #fff;
    text-decoration: none;
    font-size: 12.5px;
    font-weight: 600;
  }
  .btn:hover { background: #4f46e5; }
  .empty { padding: 40px; text-align: center; color: var(--muted); }
  footer { margin-top: 18px; font-size: 12.5px; color: var(--muted); line-height: 1.6; }
  @media (max-width: 800px) {
    .stats { grid-template-columns: repeat(2, 1fr); }
    header h1 { font-size: 24px; }
  }
</style>
</head>
<body>
<header>
  <div class="eyebrow">Retention agent · PayPal sandbox</div>
  <h1>ChurnGuard Agent</h1>
  <p>Rule-based decisions read from __SOURCE__</p>
</header>
<main>
  <section class="stats">
    <div class="stat" style="--accent:#818cf8"><div class="num">__TOTAL__</div><div class="label">Subscribers scored</div></div>
    <div class="stat" style="--accent:#2dd4bf"><div class="num">__OFFERS__</div><div class="label">Offers created</div></div>
    <div class="stat" style="--accent:#94a3b8"><div class="num">__LOGGED__</div><div class="label">Logged only</div></div>
    <div class="stat" style="--accent:#fb7185"><div class="num">__ERRORS__</div><div class="label">PayPal errors</div></div>
  </section>
  <section class="panel">
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Time (UTC)</th><th>Subscriber</th><th>Risk</th><th>Failed</th>
            <th>Action</th><th>Reason</th><th>Status</th><th>PayPal order</th><th>Offer</th>
          </tr>
        </thead>
        <tbody>__ROWS__</tbody>
      </table>
    </div>
  </section>
  <footer>
    Only the sandbox buyer account triggers a PayPal call. Other rows are demo subscribers and are logged only.
    Offers are unpaid sandbox orders; the approval page is the evidence of the offer.
  </footer>
</main>
</body>
</html>
"""


def load_decisions():
    if not DECISIONS.exists():
        return []
    return [json.loads(line) for line in DECISIONS.read_text().splitlines() if line.strip()]


def esc(value):
    return html.escape("" if value is None else str(value))


def risk_cell(value):
    try:
        fraction = max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return esc(value)
    pct = fraction * 100
    return (
        '<div class="risk">'
        f'<div class="risk-bar"><span style="width:{pct:.0f}%"></span></div>'
        f"<span>{fraction:.2f}</span>"
        "</div>"
    )


def build_row(r):
    badge_cls, badge_label = ACTION_STYLE.get(r.get("action") or "", ("badge badge-gray", r.get("action") or "unknown"))
    pill_cls, pill_label = STATUS_STYLE.get(r.get("status") or "", ("pill pill-gray", r.get("status") or "unknown"))

    order_id = r.get("order_id")
    order_cell = esc(order_id) if order_id else '<span class="muted">n/a</span>'

    offer_amount = r.get("offer_amount")
    amount_text = ("$" + esc(offer_amount) + " USD") if offer_amount else '<span class="muted">n/a</span>'

    link = ""
    if r.get("approve_url"):
        link = f'<br><a class="btn" href="{esc(r["approve_url"])}" target="_blank" rel="noopener">Open offer</a>'

    return (
        "<tr>"
        f'<td class="mono">{esc(r.get("time"))}</td>'
        f'<td class="subject">{esc(r.get("subscriber"))}</td>'
        f"<td>{risk_cell(r.get('risk_score'))}</td>"
        f'<td class="mono">{esc(r.get("failed_payments"))}</td>'
        f'<td><span class="{badge_cls}">{esc(badge_label)}</span></td>'
        f'<td class="reason">{esc(r.get("reason"))}</td>'
        f'<td><span class="{pill_cls}">{esc(pill_label)}</span></td>'
        f'<td class="mono">{order_cell}</td>'
        f"<td>{amount_text}{link}</td>"
        "</tr>"
    )


@app.get("/")
def index():
    rows = load_decisions()
    orders = sum(1 for r in rows if r.get("status") == "order_created")
    errors = sum(1 for r in rows if r.get("status") == "paypal_error")
    logged = sum(1 for r in rows if r.get("status") == "logged_only")

    body = "".join(build_row(r) for r in rows)
    if not body:
        body = '<tr><td class="empty" colspan="9">No decisions yet. Run python src\\agent.py first.</td></tr>'

    return (
        PAGE.replace("__SOURCE__", esc(DECISIONS))
        .replace("__TOTAL__", str(len(rows)))
        .replace("__OFFERS__", str(orders))
        .replace("__LOGGED__", str(logged))
        .replace("__ERRORS__", str(errors))
        .replace("__ROWS__", body)
    )


@app.get("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(port=5001)