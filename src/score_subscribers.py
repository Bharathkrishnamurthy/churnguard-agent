import joblib
import pandas as pd
from pathlib import Path

PROFILES = Path("data/subscriber_profiles.csv")
OUT = Path("data/scored_subscribers.csv")
MODEL = Path("models/churn_model.joblib")
FEATURES = ["tenure", "MonthlyCharges", "TotalCharges", "Contract",
            "PaymentMethod", "InternetService", "PaperlessBilling"]

model = joblib.load(MODEL)
profiles = pd.read_csv(PROFILES)
profiles["risk_score"] = model.predict_proba(profiles[FEATURES])[:, 1].round(4)
profiles.to_csv(OUT, index=False)

print(profiles[["email", "risk_score", "failed_payments"]].to_string(index=False))
print("all scores between 0 and 1:", profiles["risk_score"].between(0, 1).all())
print("distinct scores:", profiles["risk_score"].nunique())
