import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest


# ----------------------------
# 1. Load vendor profiles
# ----------------------------
vendors = pd.read_csv("../data/vendor_profiles.csv")

# Example weights for controls (tweak as needed)
weights = {
    "DataSensitivity": 2.0,
    "MFA": -1.0,         # reduces risk
    "Encryption": -1.0,  # reduces risk
    "Certifications": -0.5,
    "SLA": -0.5,
    "ComplianceGaps": 2.0
}

def compute_base_risk(row):
    score = 0
    for col, w in weights.items():
        score += row[col] * w
    return max(score, 0)  # risk score cannot be negative

vendors["BaseRisk"] = vendors.apply(compute_base_risk, axis=1)

# ----------------------------
# 2. Load access logs (optional)
# ----------------------------
try:
    logs = pd.read_csv("../data/access_logs.csv")
    anomaly_features = logs.groupby("vendor").agg({
    "success": lambda x: (x == 0).mean(),  # fail rate
    "timestamp": lambda x: np.mean([pd.to_datetime(t).hour not in range(8,18) for t in x]),  # after-hours %
    "country": "nunique"  # geo diversity
}).reset_index()


    anomaly_features.columns = ["Vendor", "FailRate", "AfterHours", "GeoSpread"]

    # Normalize (z-scores)
    zscores = (anomaly_features[["FailRate", "AfterHours", "GeoSpread"]] - 
            anomaly_features[["FailRate", "AfterHours", "GeoSpread"]].mean()) / \
            anomaly_features[["FailRate", "AfterHours", "GeoSpread"]].std()

    anomaly_features["AnomalyBonus"] = zscores.sum(axis=1).clip(lower=0) * 5

    vendors = vendors.merge(anomaly_features[["Vendor","AnomalyBonus"]], on="Vendor", how="left")
    vendors["AnomalyBonus"] = vendors["AnomalyBonus"].fillna(0)

except FileNotFoundError:
    vendors["AnomalyBonus"] = 0

# ----------------------------
# 3. Total risk and levels
# ----------------------------
vendors["TotalRisk"] = vendors["BaseRisk"] + vendors["AnomalyBonus"]

# Risk level by tertiles
vendors["RiskLevel"] = pd.qcut(vendors["TotalRisk"], q=3, labels=["Low","Medium","High"])

# ----------------------------
# 4. Save results
# ----------------------------
vendors.to_csv("../outputs/vendor_risk_scores.csv", index=False)

# ----------------------------
# 5. Charts
# ----------------------------
plt.figure(figsize=(8,5))
plt.bar(vendors["Vendor"], vendors["TotalRisk"], color="red")
plt.title("Vendor Total Risk Scores")
plt.ylabel("Risk Score")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("../outputs/vendor_risk_scores_bar.png")
plt.close()

plt.figure(figsize=(5,5))
vendors["RiskLevel"].value_counts().plot.pie(autopct='%1.0f%%')
plt.title("Risk Level Distribution")
plt.ylabel("")
plt.savefig("../outputs/risk_level_counts.png")
plt.close()

print("✅ Risk scoring complete. Check ../outputs for results.")


# ----------------------------
# 6. AI-driven Anomaly Detection
# ----------------------------
if "Vendor" in vendors.columns:
    print("🤖 Running AI-driven anomaly detection...")
    # Example features for AI: TotalRisk + anomalies from logs
    X = vendors[["TotalRisk"]].values  

    iso = IsolationForest(contamination=0.2, random_state=42)
    preds = iso.fit_predict(X)

    vendors["AI_Anomaly"] = ["Yes" if p == -1 else "No" for p in preds]

    # Save again with AI anomaly column
    vendors.to_csv("../outputs/vendor_risk_scores.csv", index=False)

    print("🤖 AI anomaly detection added. Updated results saved.")

