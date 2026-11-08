import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

DATA = Path("data/WA_Fn-UseC_-Telco-Customer-Churn.csv")
OUT = Path("models")
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA)
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df = df.dropna(subset=["TotalCharges"])
y = (df["Churn"] == "Yes").astype(int)

# Features chosen to match what PayPal subscription data can provide
NUMERIC = ["tenure", "MonthlyCharges", "TotalCharges"]
CATEGORICAL = ["Contract", "PaymentMethod", "InternetService", "PaperlessBilling"]
X = df[NUMERIC + CATEGORICAL]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

preprocess = ColumnTransformer([
    ("num", "passthrough", NUMERIC),
    ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
])
model = Pipeline([
    ("preprocess", preprocess),
    ("rf", RandomForestClassifier(
        n_estimators=300, class_weight="balanced", random_state=42)),
])
model.fit(X_train, y_train)
pred = model.predict(X_test)

# Baseline: always predict "no churn". The model must beat this to be useful.
baseline_accuracy = 1 - y_test.mean()

feature_names = model.named_steps["preprocess"].get_feature_names_out()
importances = model.named_steps["rf"].feature_importances_
top = sorted(zip(feature_names, importances), key=lambda t: t[1], reverse=True)[:10]

metrics = {
    "dataset": DATA.name,
    "dataset_note": "Public telecom dataset, not PayPal data. Used to prototype the model.",
    "rows_total": int(len(df)),
    "rows_test": int(len(y_test)),
    "accuracy": round(accuracy_score(y_test, pred), 4),
    "precision": round(precision_score(y_test, pred), 4),
    "recall": round(recall_score(y_test, pred), 4),
    "f1": round(f1_score(y_test, pred), 4),
    "baseline_accuracy_always_no_churn": round(baseline_accuracy, 4),
    "top_features": [{"feature": f, "importance": round(float(i), 4)} for f, i in top],
}

joblib.dump(model, OUT / "churn_model.joblib")
(OUT / "metrics.json").write_text(json.dumps(metrics, indent=2))
print(json.dumps(metrics, indent=2))