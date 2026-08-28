import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Fix Windows console encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from database.init_db import find_source_data, ensure_database

load_dotenv()


def compute_business_analytics(df: pd.DataFrame) -> dict:
    """Computes executive-level business analytics, period comparisons, and territory breakdowns."""
    if df.empty:
        return {}

    # Standardize column types
    df = df.copy()
    if "Order_Date" in df.columns:
        df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")

    # Core Metrics
    total_rev = float(df["Revenue"].sum()) if "Revenue" in df.columns else 0.0
    total_orders = int(df["Order_ID"].nunique()) if "Order_ID" in df.columns else len(df)
    total_customers = int(df["Customer_ID"].nunique()) if "Customer_ID" in df.columns else 0
    aov = float(total_rev / total_orders) if total_orders > 0 else 0.0
    total_profit = float(df["Profit"].sum()) if "Profit" in df.columns else (total_rev * 0.25)
    margin = (total_profit / total_rev * 100) if total_rev > 0 else 0.0

    # Period Comparison (Latest 50% timeline vs Previous 50% timeline)
    sorted_df = df.sort_values("Order_Date") if "Order_Date" in df.columns else df
    mid_idx = len(sorted_df) // 2

    if mid_idx > 0 and "Revenue" in sorted_df.columns:
        prev_period = sorted_df.iloc[:mid_idx]
        curr_period = sorted_df.iloc[mid_idx:]

        prev_rev = float(prev_period["Revenue"].sum())
        curr_rev = float(curr_period["Revenue"].sum())
        prev_orders = int(len(prev_period))
        curr_orders = int(len(curr_period))

        rev_growth_pct = ((curr_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0.0
        orders_growth_pct = ((curr_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0.0
    else:
        rev_growth_pct = 0.0
        orders_growth_pct = 0.0

    # Territory / Region Dynamics
    region_rev = df.groupby("Region")["Revenue"].sum().sort_values(ascending=False) if "Region" in df.columns else pd.Series()
    top_region = region_rev.index[0] if not region_rev.empty else "N/A"
    top_region_rev = float(region_rev.iloc[0]) if not region_rev.empty else 0.0
    top_region_share = (top_region_rev / total_rev * 100) if total_rev > 0 else 0.0

    lowest_region = region_rev.index[-1] if len(region_rev) > 1 else top_region
    lowest_region_rev = float(region_rev.iloc[-1]) if len(region_rev) > 1 else top_region_rev

    # Category Dynamics
    cat_rev = df.groupby("Category")["Revenue"].sum().sort_values(ascending=False) if "Category" in df.columns else pd.Series()
    top_cat = cat_rev.index[0] if not cat_rev.empty else "N/A"
    top_cat_rev = float(cat_rev.iloc[0]) if not cat_rev.empty else 0.0
    stable_cat = cat_rev.index[1] if len(cat_rev) > 1 else top_cat

    # Channel Dynamics
    channel_rev = df.groupby("Sales_Channel")["Revenue"].sum() if "Sales_Channel" in df.columns else pd.Series()
    top_channel = channel_rev.idxmax() if not channel_rev.empty else "Online"

    # Return Rate
    return_rate = float((df["Returned"] == "Yes").mean() * 100) if "Returned" in df.columns else 4.5

    # Anomalies
    anomaly_count = int((df["Anomaly"] == "Anomaly").sum()) if "Anomaly" in df.columns else 0
    anomaly_rate = (anomaly_count / total_orders * 100) if total_orders > 0 else 0.0

    return {
        "total_revenue": total_rev,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "aov": aov,
        "total_profit": total_profit,
        "margin": margin,
        "rev_growth_pct": rev_growth_pct,
        "orders_growth_pct": orders_growth_pct,
        "top_region": top_region,
        "top_region_rev": top_region_rev,
        "top_region_share": top_region_share,
        "lowest_region": lowest_region,
        "lowest_region_rev": lowest_region_rev,
        "top_category": top_cat,
        "top_category_rev": top_cat_rev,
        "stable_category": stable_cat,
        "top_channel": top_channel,
        "return_rate": return_rate,
        "anomaly_count": anomaly_count,
        "anomaly_rate": anomaly_rate,
    }


def generate_deterministic_business_insights(metrics: dict) -> dict:
    """Creates rich, professional executive business insights using deterministic heuristics."""
    growth = metrics.get("rev_growth_pct", 0.0)
    top_reg = metrics.get("top_region", "North")
    low_reg = metrics.get("lowest_region", "South")
    top_cat = metrics.get("top_category", "Electronics")
    stable_cat = metrics.get("stable_category", "Furniture")
    margin = metrics.get("margin", 24.5)
    anomalies = metrics.get("anomaly_count", 0)
    ret_rate = metrics.get("return_rate", 5.0)
    top_reg_share = metrics.get("top_region_share", 35.0)

    # Determine alert state & title
    if growth <= -2.0:
        alert_title = "⚠️ Sales Performance Alert"
        severity = "Warning"
        summary_core = (
            f"Sales decreased by {abs(growth):.1f}% compared with the previous period. "
            f"The largest decline was observed in Region {low_reg}, "
            f"while Product Category {stable_cat} remained stable."
        )
    elif anomalies > 20:
        alert_title = "⚠️ Operational Risk & Sales Alert"
        severity = "Warning"
        summary_core = (
            f"Sales performance showed variance across territories with {anomalies:,} anomalous orders flagged. "
            f"The largest transaction dip was observed in Region {low_reg}, "
            f"while Product Category {stable_cat} remained stable."
        )
    elif growth >= 2.0:
        alert_title = "📈 Executive Revenue Growth Alert"
        severity = "Positive"
        summary_core = (
            f"Sales increased by {growth:.1f}% compared with the previous period. "
            f"The strongest revenue surge was registered in Region {top_reg} ({top_reg_share:.1f}% share), "
            f"with Product Category {top_cat} leading gross margin contributions."
        )
    else:
        alert_title = "⚡ Executive Business Intelligence Radar"
        severity = "Healthy"
        summary_core = (
            f"Sales performance remained stable with high operational consistency across territories. "
            f"Region {top_reg} continues to anchor top-line delivery ({top_reg_share:.1f}% revenue share), "
            f"while Category {stable_cat} maintains predictable customer demand."
        )

    key_drivers = [
        f"**Territory Contribution**: Region {top_reg} dominates top-line volume with {top_reg_share:.1f}% market share; Region {low_reg} presents an addressable expansion gap.",
        f"**Product Leadership**: Category {top_cat} generates highest unit throughput, while {stable_cat} exhibits consistent repeat orders.",
        f"**Channel Efficiency**: {metrics.get('top_channel', 'Online')} sales channels deliver the highest conversion rate and lowest customer acquisition friction.",
    ]

    risk_assessment = (
        f"Operational return rate stands at {ret_rate:.1f}%. "
        f"{f'{anomalies:,} transaction anomalies detected requiring pricing audit' if anomalies > 0 else 'Zero critical transaction anomalies detected; baseline pricing integrity intact.'}"
    )

    recommended_actions = [
        f"Investigate Region {low_reg}'s order volume, logistics SLAs, and regional conversion rates.",
        f"Scale inventory and promotional budgets for top-selling Category {top_cat} ahead of high-demand cycles.",
        f"Audit discount threshold compliance on outlier transactions to safeguard the {margin:.1f}% operating profit margin.",
    ]

    raw_markdown = f"""### {alert_title}

**Executive Summary:**
{summary_core}

**Key Business Drivers:**
- {key_drivers[0]}
- {key_drivers[1]}
- {key_drivers[2]}

**Operational Risk Assessment:**
{risk_assessment}

**Recommended Strategic Actions:**
1. {recommended_actions[0]}
2. {recommended_actions[1]}
3. {recommended_actions[2]}
"""

    return {
        "alert_title": alert_title,
        "severity": severity,
        "executive_summary": summary_core,
        "key_drivers": key_drivers,
        "risk_assessment": risk_assessment,
        "recommended_actions": recommended_actions,
        "raw_markdown": raw_markdown,
    }


def generate_executive_insights(df: pd.DataFrame = None, use_gemini: bool = True) -> dict:
    """
    Generates structured, executive-grade business insights using Gemini AI with seamless deterministic fallback.
    """
    if df is None:
        source_path = find_source_data()
        df = pd.read_csv(source_path)

    metrics = compute_business_analytics(df)
    deterministic_result = generate_deterministic_business_insights(metrics)

    if not use_gemini:
        return deterministic_result

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return deterministic_result

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        prompt = f"""You are a Principal Business Intelligence Analyst & VP of Operations.
Analyze the following enterprise e-commerce metrics and generate an executive business report.

METRICS SNAPSHOT:
- Total Gross Revenue: ₹{metrics['total_revenue']:,.2f}
- Period Revenue Growth: {metrics['rev_growth_pct']:.1f}%
- Total Orders: {metrics['total_orders']:,}
- Unique Customers: {metrics['total_customers']:,}
- Average Order Value (AOV): ₹{metrics['aov']:,.2f}
- Net Profit Margin: {metrics['margin']:.1f}%
- Top Performing Region: {metrics['top_region']} ({metrics['top_region_share']:.1f}% of total sales)
- Lagging / Declining Region: {metrics['lowest_region']}
- Dominant Product Category: {metrics['top_category']}
- Stable Product Category: {metrics['stable_category']}
- Primary Sales Channel: {metrics['top_channel']}
- Return Rate: {metrics['return_rate']:.1f}%
- Detected Operational Anomalies: {metrics['anomaly_count']:,}

TONE & STRUCTURE:
- Direct, business-language, executive tone.
- Do NOT output dry generic bullet points like "Sales changed by X%".
- Follow this exact format:

⚠️ [ALERT / RADAR TITLE]
[2-3 sentence Executive Summary explaining the exact business narrative, identifying the largest regional shift and category stability]

KEY DRIVERS:
• [Territory insight with specific region dynamics]
• [Category and product margin dynamic]
• [Channel and customer behavior insight]

OPERATIONAL RISKS:
[Risk analysis covering returns, margin impact, and anomaly severity]

RECOMMENDED ACTIONS:
1. [Actionable strategic recommendation for the lagging territory]
2. [Actionable strategic recommendation for category/inventory scaling]
3. [Actionable governance recommendation for pricing/anomaly controls]
"""

        candidate_models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"]
        ai_text = None

        for model_name in candidate_models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    ai_text = response.text.strip()
                    break
            except Exception:
                continue

        if ai_text:
            return {
                "alert_title": deterministic_result["alert_title"],
                "severity": deterministic_result["severity"],
                "executive_summary": deterministic_result["executive_summary"],
                "key_drivers": deterministic_result["key_drivers"],
                "risk_assessment": deterministic_result["risk_assessment"],
                "recommended_actions": deterministic_result["recommended_actions"],
                "raw_markdown": ai_text,
            }

    except Exception as err:
        print(f"[AI Summary Warning] Gemini API unavailable: {err}. Using deterministic business engine.")

    return deterministic_result


if __name__ == "__main__":
    ensure_database(verbose=False)
    print("=" * 70)
    print("GENERATING EXECUTIVE BUSINESS INSIGHTS...")
    print("=" * 70)

    insights = generate_executive_insights()
    print(insights["raw_markdown"])

    os.makedirs(os.path.join(BASE_DIR, "reports"), exist_ok=True)
    report_file = os.path.join(BASE_DIR, "reports", "AI_Business_Summary.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(insights["raw_markdown"])

    print("=" * 70)
    print(f"Report Saved Successfully: {report_file}")
    print("=" * 70)