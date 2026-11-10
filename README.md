# ChurnGuard Agent

A rule-based retention agent for PayPal subscriptions. It scores subscribers with a churn model, chooses one action from fixed rules, creates a discounted PayPal sandbox order for the highest-risk case, and logs every decision. Each decision has a one-sentence explanation from a language model, with a rule-based fallback.

## Quick view (no credentials needed)

    pip install -r requirements.txt
    set DECISIONS_PATH=samples/decisions.jsonl
    python src/dashboard.py

Open http://127.0.0.1:5001. The page shows the sample decision log. The hosted demo is at https://churnguard-agent.onrender.com.

## Full run (needs PayPal sandbox and Gemini keys)

1. Create a `.env` file with `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, `PAYPAL_ENVIRONMENT=SANDBOX`, `SANDBOX_BUYER_EMAIL`, and optionally `GEMINI_API_KEY`. Never commit this file.
2. Train the model: `python src/train_model.py` (needs the public Telco CSV in `data/`).
3. Score the profiles: `python src/make_profiles.py`, then `python src/score_subscribers.py`.
4. Run the agent: `python src/agent.py`. Add `--dry-run` to skip PayPal calls.

## Tools used

PayPal sandbox (Orders API, Subscriptions, webhooks), scikit-learn (Random Forest), Flask and Gunicorn, Google Gemini API (explanations only), Render (hosting).

## Limits

- Churn model is a prototype trained on public telecom data, not PayPal data.
- Failed-payment counts are demo values.
- Hosted dashboard shows a saved snapshot, not live decisions.
- Signed subscription events are not yet tested end to end.

## Licence

MIT. See LICENSE.
