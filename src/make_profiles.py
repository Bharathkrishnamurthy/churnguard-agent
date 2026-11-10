import pandas as pd
from pathlib import Path

SRC = Path("data/WA_Fn-UseC_-Telco-Customer-Churn.csv")
OUT = Path("data/subscriber_profiles.csv")
BUYER = "sb-n51gg53750635@personal.example.com"
FEATURES = ["tenure", "MonthlyCharges", "TotalCharges", "Contract",
            "PaymentMethod", "InternetService", "PaperlessBilling"]

df = pd.read_csv(SRC)
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df = df.dropna(subset=["TotalCharges"])

picked = pd.concat([
    df[df["Churn"] == "Yes"].sample(2, random_state=7),
    df[df["Churn"] == "No"].sample(2, random_state=7),
]).reset_index(drop=True)

profiles = picked[FEATURES].copy()
profiles.insert(0, "email", [
    BUYER,
    "demo-subscriber-2@example.com",
    "demo-subscriber-3@example.com",
    "demo-subscriber-4@example.com",
])
profiles["failed_payments"] = [2, 0, 0, 0]
profiles["outstanding_amount"] = "10.00"
profiles["profile_source"] = "Telco row, demo profile"

profiles.to_csv(OUT, index=False)
print("rows written:", len(profiles))
