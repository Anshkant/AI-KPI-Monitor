import os
import pandas as pd
from dotenv import load_dotenv
from google import genai

# ==========================
# Load API Key
# ==========================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

# ==========================
# Load Dataset
# ==========================

clean_path = "data/processed/clean_sales_data.csv"
if not os.path.exists(clean_path) and os.path.exists(clean_path + ".gz"):
    clean_path += ".gz"

df = pd.read_csv(clean_path)




# ==========================
# Business KPIs
# ==========================

total_revenue = df["Revenue"].sum()
total_orders = df["Order_ID"].nunique()
total_customers = df["Customer_ID"].nunique()
avg_order = total_revenue / total_orders

top_category = (
    df.groupby("Category")["Revenue"]
    .sum()
    .idxmax()
)

top_region = (
    df.groupby("Region")["Revenue"]
    .sum()
    .idxmax()
)

return_rate = (
    (df["Returned"] == "Yes").mean()
) * 100

# ==========================
# Prompt
# ==========================

prompt = f"""
You are a Senior Business Analyst.

Analyze the following business metrics.

Total Revenue:
₹{df["Revenue"].sum():,.2f}

Total Orders:
{len(df)}

Average Order Value:
₹{df["Revenue"].mean():,.2f}

Top Category:
{df.groupby("Category")["Revenue"].sum().idxmax()}

Top Region:
{df.groupby("Region")["Revenue"].sum().idxmax()}

Return Rate:
{round((df["Returned"]=="Yes").mean()*100,2)}%

Write a professional report with:

1 Executive Summary

2 Key Insights

3 Business Risks

4 Recommendations

Maximum 250 words.
"""
# ==========================
# Generate AI Summary
# ==========================

try:

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    summary = response.text

except Exception as e:

    summary = f"""
AI Summary could not be generated.

Reason:
{e}

Fallback Summary

• Revenue generated successfully.

• Orders processed successfully.

• Business performance appears healthy.

• Review return rate.

• Focus on highest revenue region.

• Increase sales of top category.
"""
print("="*70)
print(summary)

# ==========================
# Save Report
# ==========================

os.makedirs("reports", exist_ok=True)

with open(
    "reports/AI_Business_Summary.txt",
    "w",
    encoding="utf-8"
) as f:

    f.write(summary)

print("\nReport Saved Successfully")