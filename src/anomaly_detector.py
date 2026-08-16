import os
import pandas as pd
from sklearn.ensemble import IsolationForest


# ============================================================
# LOAD CLEAN DATASET
# ============================================================

clean_path = "data/processed/clean_sales_data.csv"
if not os.path.exists(clean_path) and os.path.exists(clean_path + ".gz"):
    clean_path += ".gz"

df = pd.read_csv(clean_path)



# ============================================================
# FEATURES FOR ANOMALY DETECTION
# ============================================================

features = df[
    [
        "Revenue",
        "Quantity"
    ]
].copy()


# Make sure numeric values are valid

features["Revenue"] = pd.to_numeric(
    features["Revenue"],
    errors="coerce"
)

features["Quantity"] = pd.to_numeric(
    features["Quantity"],
    errors="coerce"
)


# Replace missing values

features = features.fillna(
    features.median()
)


# ============================================================
# TRAIN ISOLATION FOREST
# ============================================================

model = IsolationForest(
    n_estimators=100,
    contamination=0.02,
    random_state=42
)


# ============================================================
# PREDICT ANOMALIES
# ============================================================

df["Anomaly_Label"] = model.fit_predict(
    features
)


# ============================================================
# ANOMALY SCORE
# ============================================================

# Isolation Forest decision_function:
# Lower value = more anomalous

df["Anomaly_Score"] = (
    -model.decision_function(features)
)


# ============================================================
# BASIC ANOMALY LABEL
# ============================================================

df["Anomaly"] = df[
    "Anomaly_Label"
].map(
    {
        1: "Normal",
        -1: "Anomaly"
    }
)


# ============================================================
# CALCULATE ANOMALY SCORE THRESHOLDS
# ============================================================

anomaly_scores = df.loc[
    df["Anomaly"] == "Anomaly",
    "Anomaly_Score"
]


if len(anomaly_scores) > 0:

    critical_threshold = anomaly_scores.quantile(
        0.75
    )

    high_threshold = anomaly_scores.quantile(
        0.40
    )

else:

    critical_threshold = 0
    high_threshold = 0


# ============================================================
# ANOMALY SEVERITY
# ============================================================

def calculate_severity(row):

    if row["Anomaly"] == "Normal":

        return "Normal"

    score = row["Anomaly_Score"]

    if score >= critical_threshold:

        return "Critical"

    elif score >= high_threshold:

        return "High"

    else:

        return "Medium"


df["Anomaly_Severity"] = df.apply(
    calculate_severity,
    axis=1
)


# ============================================================
# BUSINESS REASON DETECTION
# ============================================================

revenue_q1 = features["Revenue"].quantile(
    0.25
)

revenue_q3 = features["Revenue"].quantile(
    0.75
)

revenue_iqr = (
    revenue_q3 - revenue_q1
)


revenue_lower = (
    revenue_q1 - 1.5 * revenue_iqr
)

revenue_upper = (
    revenue_q3 + 1.5 * revenue_iqr
)


quantity_q1 = features["Quantity"].quantile(
    0.25
)

quantity_q3 = features["Quantity"].quantile(
    0.75
)

quantity_iqr = (
    quantity_q3 - quantity_q1
)


quantity_lower = (
    quantity_q1 - 1.5 * quantity_iqr
)

quantity_upper = (
    quantity_q3 + 1.5 * quantity_iqr
)


# ============================================================
# GENERATE ANOMALY REASON
# ============================================================

def generate_reason(row):

    if row["Anomaly"] == "Normal":

        return "Normal transaction"


    revenue = row["Revenue"]
    quantity = row["Quantity"]


    revenue_unusual = (
        revenue < revenue_lower
        or
        revenue > revenue_upper
    )


    quantity_unusual = (
        quantity < quantity_lower
        or
        quantity > quantity_upper
    )


    if revenue_unusual and quantity_unusual:

        return (
            "Unusual revenue and quantity"
        )


    elif revenue_unusual:

        if revenue < revenue_lower:

            return (
                "Unusually low revenue"
            )

        else:

            return (
                "Unusually high revenue"
            )


    elif quantity_unusual:

        return (
            "Unusual order quantity"
        )


    return (
        "Unusual transaction pattern"
    )


df["Anomaly_Reason"] = df.apply(
    generate_reason,
    axis=1
)


# ============================================================
# CLEAN TEMPORARY COLUMN
# ============================================================

df.drop(
    columns=[
        "Anomaly_Label"
    ],
    inplace=True
)


# ============================================================
# SAVE OUTPUT
# ============================================================

os.makedirs(
    "data/processed",
    exist_ok=True
)


output_path = (
    "data/processed/anomaly_sales_data.csv"
)


df.to_csv(
    output_path,
    index=False
)


# ============================================================
# TERMINAL REPORT
# ============================================================

print("=" * 65)

print(
    "AI KPI MONITOR - ANOMALY DETECTION"
)

print("=" * 65)


print(
    "\nTotal Records :",
    len(df)
)


print(
    "Normal :",
    (
        df["Anomaly"] == "Normal"
    ).sum()
)


print(
    "Anomalies :",
    (
        df["Anomaly"] == "Anomaly"
    ).sum()
)


print("\nSeverity Breakdown")

print(
    df["Anomaly_Severity"]
    .value_counts()
)


print("\nReason Breakdown")

print(
    df["Anomaly_Reason"]
    .value_counts()
)


print("\nTop Critical Anomalies")


critical = df[
    df["Anomaly_Severity"]
    == "Critical"
]


print(
    critical[
        [
            "Order_ID",
            "Revenue",
            "Quantity",
            "Anomaly_Severity",
            "Anomaly_Reason"
        ]
    ].head(10)
)


print(
    "\nDataset Saved Successfully:"
)

print(
    output_path
)


print("=" * 65)