import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
import sys
import sqlite3
import statistics
from datetime import date, datetime, timedelta

# Project root path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.init_db import ensure_database, is_database_initialized, DB_PATH
from src.live_data_generator import generate_single_order, get_template_df

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI KPI Monitor | Executive Live Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# API CONFIGURATION
# ============================================================

# Auto-detect local vs deployed URL (supports Streamlit Secrets)
default_api_url = "http://127.0.0.1:8000"
try:
    if hasattr(st, "secrets") and "API_BASE_URL" in st.secrets:
        default_api_url = st.secrets["API_BASE_URL"]
except Exception:
    pass

if not default_api_url or default_api_url == "http://127.0.0.1:8000":
    default_api_url = os.getenv("API_BASE_URL", "https://ai-kpi-monitor.onrender.com" if not os.path.exists(os.path.join(BASE_DIR, "venv")) else "http://127.0.0.1:8000")

if "api_url" not in st.session_state:
    st.session_state["api_url"] = default_api_url

API_BASE_URL = st.session_state["api_url"].rstrip("/")

SALES_API = f"{API_BASE_URL}/sales"
SUMMARY_API = f"{API_BASE_URL}/sales/dashboard-summary"
FILTER_OPTIONS_API = f"{API_BASE_URL}/sales/filter-options"
LATEST_API = f"{API_BASE_URL}/sales/latest"
LATEST_ONE_API = f"{API_BASE_URL}/sales/latest-one"
ANOMALY_API = f"{API_BASE_URL}/anomalies/latest"
AI_INSIGHTS_API = f"{API_BASE_URL}/ai/executive-insights"
TRIGGER_API = f"{API_BASE_URL}/generator/trigger"
GENERATOR_STATUS_API = f"{API_BASE_URL}/generator/status"


# ============================================================
# SVG ICONS LIBRARY (Clean, Minimalist, Enterprise Grade)
# ============================================================

ICONS = {
    "revenue": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>""",
    "orders": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>""",
    "customers": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>""",
    "aov": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>""",
    "profit": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>""",
    "margin": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0D9488" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path></svg>""",
    "server": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>""",
    "database": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>""",
    "calendar": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>""",
    "zap": """<svg width="16" height="16" viewBox="0 0 24 24" fill="#F59E0B" stroke="#D97706" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>""",
    "shield_alert": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E11D48" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>""",
    "sparkles": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4F46E5" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"></path></svg>""",
    "activity": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0284C7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>""",
    "layers": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4F46E5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>""",
    "chart": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>""",
    "pie": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0284C7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path></svg>""",
}


# ============================================================
# MODERN ENTERPRISE CSS STYLES
# ============================================================

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #0f172a;
        }

        /* Top Header Brand */
        .brand-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            padding-bottom: 0.8rem;
            border-bottom: 1px solid #e2e8f0;
        }

        .brand-title-wrap {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .brand-logo-badge {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
        }

        .brand-title {
            font-size: 1.65rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            color: #0f172a;
            margin: 0;
            line-height: 1.2;
        }

        .brand-subtitle {
            font-size: 0.86rem;
            color: #64748b;
            font-weight: 500;
            margin: 0;
        }

        /* Live Status Badge */
        .live-status-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 600;
            background: #ecfdf5;
            color: #065f46;
            border: 1px solid #a7f3d0;
            box-shadow: 0 1px 3px rgba(16, 185, 129, 0.1);
        }

        .live-pulse-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #10b981;
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
            animation: pulse-ring 1.8s infinite;
        }

        @keyframes pulse-ring {
            0% {
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
            }
            70% {
                transform: scale(1);
                box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
            }
            100% {
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
            }
        }

        /* Custom Modern KPI Card */
        .kpi-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 4px 12px rgba(0, 0, 0, 0.02);
            transition: all 0.25s ease;
            position: relative;
            overflow: hidden;
            margin-bottom: 12px;
        }

        .kpi-top-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }

        .kpi-label {
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #64748b;
        }

        .kpi-icon-box {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 36px;
            height: 36px;
            border-radius: 10px;
        }

        .kpi-metric-val {
            font-size: 1.85rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            color: #0f172a;
            margin-bottom: 4px;
            line-height: 1.15;
        }

        .kpi-footer-sub {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.78rem;
            font-weight: 500;
            color: #64748b;
        }

        /* System Info Card */
        .sys-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 10px;
        }

        .sys-icon-box {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 38px;
            height: 38px;
            border-radius: 10px;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
        }

        .sys-label {
            font-size: 0.76rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            margin-bottom: 2px;
        }

        .sys-val {
            font-size: 1.1rem;
            font-weight: 700;
            color: #0f172a;
        }

        /* Live Transaction Ribbon */
        .tx-ribbon {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #3b82f6;
            border-radius: 8px;
            padding: 12px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 10px 0 16px 0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        }

        .tx-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .tx-pill {
            background: #dbeafe;
            color: #1e40af;
            font-size: 0.76rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
        }

        .tx-meta {
            font-size: 0.88rem;
            color: #334155;
        }

        .tx-amount {
            font-size: 1rem;
            font-weight: 700;
            color: #059669;
        }

        /* Section Headers */
        .section-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 20px 0 12px 0;
            padding-bottom: 6px;
            border-bottom: 1px solid #f1f5f9;
        }

        .section-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #1e293b;
            letter-spacing: -0.02em;
            margin: 0;
        }

        /* Anomaly Alert Cards */
        .alert-card {
            background: #ffffff;
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .alert-critical {
            border: 1px solid #fecdd3;
            border-left: 4px solid #e11d48;
            background: #fff1f2;
        }

        .alert-high {
            border: 1px solid #fed7aa;
            border-left: 4px solid #f97316;
            background: #fff7ed;
        }

        .alert-medium {
            border: 1px solid #fef08a;
            border-left: 4px solid #eab308;
            background: #fefce8;
        }

        .alert-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .alert-badge-crit {
            background: #e11d48;
            color: white;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 9999px;
            text-transform: uppercase;
        }

        .alert-badge-high {
            background: #f97316;
            color: white;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 9999px;
            text-transform: uppercase;
        }

        .alert-badge-med {
            background: #ca8a04;
            color: white;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 9999px;
            text-transform: uppercase;
        }

        .alert-msg {
            font-size: 0.84rem;
            color: #334155;
            line-height: 1.4;
        }

        /* Executive AI Insight Box System */
        .ai-insights-box {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 20px 24px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
            margin: 12px 0 20px 0;
            position: relative;
        }

        .ai-header-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
            padding-bottom: 8px;
            border-bottom: 1px solid #f1f5f9;
        }

        .ai-title-wrap {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .ai-badge-alert {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.78rem;
            font-weight: 700;
            background: #fff1f2;
            color: #be123c;
            border: 1px solid #fecdd3;
        }

        .ai-badge-growth {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.78rem;
            font-weight: 700;
            background: #ecfdf5;
            color: #047857;
            border: 1px solid #a7f3d0;
        }

        .ai-badge-radar {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.78rem;
            font-weight: 700;
            background: #eef2ff;
            color: #4338ca;
            border: 1px solid #c7d2fe;
        }

        .ai-narrative-card {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-left: 4px solid #4f46e5;
            border-radius: 8px;
            padding: 14px 18px;
            font-size: 0.94rem;
            line-height: 1.6;
            color: #1e293b;
            margin: 10px 0 16px 0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
        }

        .ai-driver-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 12px 14px;
            font-size: 0.84rem;
            color: #334155;
            line-height: 1.45;
            height: 100%;
        }

        .ai-action-card {
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-left: 4px solid #16a34a;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 0.84rem;
            color: #15803d;
            font-weight: 600;
            margin-bottom: 6px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION & HELPERS
# ============================================================

http = requests.Session()


def safe_float(value):
    try:
        return float(value)
    except Exception:
        return 0.0


def money(value):
    value = safe_float(value)
    if abs(value) >= 1_000_000_000:
        return f"₹{value / 1_000_000_000:.2f}B"
    if abs(value) >= 1_000_000:
        return f"₹{value / 1_000_000:.2f}M"
    if abs(value) >= 1000:
        return f"₹{value:,.0f}"
    return f"₹{value:.0f}"


def prepare_dataframe(data):
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    if "Order_Date" in df.columns:
        df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    numeric_columns = [
        "Quantity", "Unit_Price", "Discount", "Revenue", "Cost", "Profit"
    ]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)
    return df


# ============================================================
# DUAL-ENGINE QUERY HELPERS (FastAPI HTTP + Direct SQLite WAL Fallback)
# ============================================================

def get_local_db_summary(start_date=None, end_date=None, regions=None, categories=None, channels=None):
    """Direct high-speed SQLite WAL query engine (works even when FastAPI is offline or on Streamlit Cloud)."""
    try:
        ensure_database(verbose=False)
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL;")

        where_clauses = ["1=1"]
        params = []
        if start_date:
            where_clauses.append("Order_Date >= ?")
            params.append(f"{start_date} 00:00:00")
        if end_date:
            where_clauses.append("Order_Date <= ?")
            params.append(f"{end_date} 23:59:59")
        if regions:
            ph = ",".join(["?"] * len(regions))
            where_clauses.append(f"Region IN ({ph})")
            params.extend(regions)
        if categories:
            ph = ",".join(["?"] * len(categories))
            where_clauses.append(f"Category IN ({ph})")
            params.extend(categories)
        if channels:
            ph = ",".join(["?"] * len(channels))
            where_clauses.append(f"Sales_Channel IN ({ph})")
            params.extend(channels)

        where_sql = " AND ".join(where_clauses)
        cur = conn.cursor()

        # Total records
        cur.execute(f"SELECT COUNT(*) FROM sales WHERE {where_sql}", params)
        total_monitored = cur.fetchone()[0] or 0

        # KPIs
        cur.execute(f"""
            SELECT 
                COALESCE(SUM(Revenue), 0),
                COUNT(Order_ID),
                COUNT(DISTINCT Customer_ID),
                COALESCE(AVG(Revenue), 0),
                COALESCE(SUM(Profit), 0)
            FROM sales
            WHERE {where_sql}
        """, params)
        row = cur.fetchone()
        revenue = float(row[0] or 0)
        orders = int(row[1] or 0)
        customers = int(row[2] or 0)
        aov = float(row[3] or 0)
        profit = float(row[4] or 0)
        profit_margin = round((profit / revenue * 100), 2) if revenue > 0 else 0.0

        # Monthly trend
        cur.execute(f"""
            SELECT 
                strftime('%Y-%m', Order_Date) as Month,
                SUM(Revenue) as Revenue,
                SUM(Profit) as Profit
            FROM sales
            WHERE {where_sql}
            GROUP BY Month
            ORDER BY Month ASC
        """, params)
        monthly_trend = [{"Month": r[0], "Revenue": float(r[1] or 0), "Profit": float(r[2] or 0)} for r in cur.fetchall()]

        # Region breakdown
        cur.execute(f"""
            SELECT Region, SUM(Revenue) as Revenue
            FROM sales
            WHERE {where_sql}
            GROUP BY Region
            ORDER BY Revenue DESC
        """, params)
        region_breakdown = [{"Region": r[0], "Revenue": float(r[1] or 0)} for r in cur.fetchall()]

        # Category breakdown
        cur.execute(f"""
            SELECT Category, SUM(Revenue) as Revenue
            FROM sales
            WHERE {where_sql}
            GROUP BY Category
            ORDER BY Revenue DESC
        """, params)
        category_breakdown = [{"Category": r[0], "Revenue": float(r[1] or 0)} for r in cur.fetchall()]

        # Channel breakdown
        cur.execute(f"""
            SELECT Sales_Channel, SUM(Revenue) as Revenue
            FROM sales
            WHERE {where_sql}
            GROUP BY Sales_Channel
        """, params)
        channel_breakdown = [{"Sales_Channel": r[0], "Revenue": float(r[1] or 0)} for r in cur.fetchall()]

        # Top products
        cur.execute(f"""
            SELECT Product, SUM(Revenue) as Revenue, COUNT(*) as Orders
            FROM sales
            WHERE {where_sql}
            GROUP BY Product
            ORDER BY Revenue DESC
            LIMIT 5
        """, params)
        top_products = [{"Product": r[0], "Revenue": float(r[1] or 0), "Orders": int(r[2] or 0)} for r in cur.fetchall()]

        conn.close()
        return {
            "status": "success",
            "total_monitored": total_monitored,
            "engine": "Direct SQLite Engine",
            "kpis": {
                "revenue": revenue,
                "orders": orders,
                "customers": customers,
                "average_order_value": aov,
                "profit": profit,
                "profit_margin": profit_margin
            },
            "monthly_trend": monthly_trend,
            "region_breakdown": region_breakdown,
            "category_breakdown": category_breakdown,
            "channel_breakdown": channel_breakdown,
            "top_products": top_products
        }
    except Exception as e:
        print(f"Local DB query error: {e}", flush=True)
        return None


def get_local_db_anomalies(limit=10):
    try:
        ensure_database(verbose=False)
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cur = conn.cursor()

        cur.execute("SELECT Revenue, Quantity FROM sales WHERE Revenue IS NOT NULL")
        rows = cur.fetchall()
        revs = [float(r[0]) for r in rows if r[0] is not None]
        qtys = [float(r[1]) for r in rows if r[1] is not None]

        rev_mean = statistics.mean(revs) if revs else 0
        rev_std = statistics.stdev(revs) if len(revs) > 1 else 0
        qty_mean = statistics.mean(qtys) if qtys else 0
        qty_std = statistics.stdev(qtys) if len(qtys) > 1 else 0

        cur.execute("""
            SELECT Order_ID, Order_Date, Customer_Name, Product, Region, Revenue, Quantity, Discount, Sales_Channel, Anomaly
            FROM sales
            WHERE Anomaly = 'Anomaly'
            ORDER BY Order_ID DESC
            LIMIT ?
        """, (limit,))
        anom_rows = cur.fetchall()

        data = []
        critical = 0
        high = 0
        medium = 0

        for r in anom_rows:
            order_id, order_date, cust, prod, reg, rev, qty, disc, chan, anom = r
            rev = float(rev or 0)
            qty = float(qty or 0)

            reasons = []
            if rev_std > 0 and abs(rev - rev_mean) > (3 * rev_std):
                reasons.append("Extremely unusual revenue value")
            if qty_std > 0 and abs(qty - qty_mean) > (3 * qty_std):
                reasons.append("Extremely unusual order quantity")
            if rev < 0:
                reasons.append("Negative revenue transaction")
            if not reasons:
                reasons.append("Statistical deviation from normal sales pattern")

            if len(reasons) >= 2 or rev < 0:
                sev = "Critical"
                critical += 1
            elif len(reasons) == 1:
                sev = "High"
                high += 1
            else:
                sev = "Medium"
                medium += 1

            data.append({
                "Order_ID": order_id,
                "Order_Date": order_date,
                "Customer_Name": cust,
                "Product": prod,
                "Region": reg,
                "Revenue": rev,
                "Quantity": qty,
                "Discount": disc,
                "Sales_Channel": chan,
                "Anomaly": anom,
                "Severity": sev,
                "Anomaly_Reason": " + ".join(reasons)
            })

        conn.close()
        return {
            "status": "success",
            "count": len(data),
            "critical": critical,
            "high": high,
            "medium": medium,
            "data": data
        }
    except Exception as e:
        print(f"Local anomalies query error: {e}", flush=True)
        return {"data": [], "critical": 0, "high": 0, "medium": 0}


def get_filter_options():
    try:
        response = http.get(FILTER_OPTIONS_API, timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    try:
        ensure_database(verbose=False)
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT Region FROM sales WHERE Region IS NOT NULL ORDER BY Region")
        regions = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT DISTINCT Category FROM sales WHERE Category IS NOT NULL ORDER BY Category")
        categories = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT DISTINCT Sales_Channel FROM sales WHERE Sales_Channel IS NOT NULL ORDER BY Sales_Channel")
        channels = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT MIN(DATE(Order_Date)), MAX(DATE(Order_Date)), COUNT(*) FROM sales")
        min_d, max_d, cnt = cur.fetchone()
        conn.close()
        return {
            "regions": regions or ["Central", "East", "International", "North", "North-East", "North-West", "South", "South-East", "South-West", "West"],
            "categories": categories or ["Appliances", "Electronics", "Furniture", "Office Supplies"],
            "channels": channels or ["Offline", "Online"],
            "min_date": str(min_d or "2023-08-07"),
            "max_date": str(max_d or datetime.now().strftime("%Y-%m-%d")),
            "total_records": cnt or 50000
        }
    except Exception as e:
        print(f"Filter options fallback error: {e}", flush=True)
        return {
            "regions": ["Central", "East", "International", "North", "North-East", "North-West", "South", "South-East", "South-West", "West"],
            "categories": ["Appliances", "Electronics", "Furniture", "Office Supplies"],
            "channels": ["Offline", "Online"],
            "min_date": "2023-08-07",
            "max_date": datetime.now().strftime("%Y-%m-%d"),
            "total_records": 50000
        }


def get_dashboard_summary(start_date=None, end_date=None, regions=None, categories=None, channels=None):
    params = {}
    if start_date:
        params["start_date"] = str(start_date)
    if end_date:
        params["end_date"] = str(end_date)
    if regions:
        params["regions"] = ",".join(regions)
    if categories:
        params["categories"] = ",".join(categories)
    if channels:
        params["channels"] = ",".join(channels)

    # 1. Attempt FastAPI HTTP Endpoint
    try:
        response = http.get(SUMMARY_API, params=params, timeout=3)
        if response.status_code == 200:
            data = response.json()
            data["engine"] = f"FastAPI Server ({API_BASE_URL})"
            return data
    except Exception as e:
        print(f"FastAPI unreachable at {SUMMARY_API}: {e}. Switching to direct SQLite engine.", flush=True)

    # 2. Seamless Direct SQLite WAL Engine Fallback
    return get_local_db_summary(start_date, end_date, regions, categories, channels)


def get_latest_orders(limit=10):
    try:
        response = http.get(LATEST_API, params={"limit": limit}, timeout=3)
        if response.status_code == 200:
            payload = response.json()
            return prepare_dataframe(payload.get("data", []))
    except Exception:
        pass

    try:
        ensure_database(verbose=False)
        conn = sqlite3.connect(DB_PATH, timeout=5)
        df = pd.read_sql_query(f"SELECT * FROM sales ORDER BY Order_ID DESC LIMIT {limit}", conn)
        conn.close()
        return prepare_dataframe(df.to_dict(orient="records"))
    except Exception as e:
        print(f"Latest orders fallback error: {e}", flush=True)
        return pd.DataFrame()


def get_latest_order():
    try:
        response = http.get(LATEST_ONE_API, timeout=3)
        if response.status_code == 200:
            payload = response.json()
            return payload.get("data")
    except Exception:
        pass

    try:
        ensure_database(verbose=False)
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT Order_ID, Order_Date, Customer_Name, Product, Revenue FROM sales ORDER BY Order_ID DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        if row:
            return {"Order_ID": row[0], "Order_Date": row[1], "Customer_Name": row[2], "Product": row[3], "Revenue": row[4]}
    except Exception:
        pass
    return None


def get_anomalies(limit=10):
    try:
        response = http.get(ANOMALY_API, params={"limit": limit}, timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"FastAPI anomalies unreachable at {ANOMALY_API}: {e}. Switching to direct SQLite engine.", flush=True)

    return get_local_db_anomalies(limit=limit)


def get_ai_insights(start_date=None, end_date=None, regions=None, categories=None, channels=None, use_gemini=False):
    params = {"use_gemini": str(use_gemini).lower()}
    if start_date:
        params["start_date"] = str(start_date)
    if end_date:
        params["end_date"] = str(end_date)
    if regions:
        params["regions"] = ",".join(regions)
    if categories:
        params["categories"] = ",".join(categories)
    if channels:
        params["channels"] = ",".join(channels)

    try:
        response = http.get(AI_INSIGHTS_API, params=params, timeout=5)
        if response.status_code == 200:
            payload = response.json()
            return payload.get("insights", {})
    except Exception:
        pass

    try:
        from src.ai_summary import generate_executive_insights
        ensure_database(verbose=False)
        conn = sqlite3.connect(DB_PATH, timeout=10)
        df = pd.read_sql_query("SELECT * FROM sales ORDER BY Order_Date ASC", conn)
        conn.close()
        return generate_executive_insights(df=df, use_gemini=False)
    except Exception as e:
        print(f"AI insights fallback error: {e}", flush=True)
        return None


def trigger_live_order_api(count=1):
    try:
        response = http.post(f"{TRIGGER_API}?count={count}", timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    try:
        template_df = get_template_df()
        orders = [generate_single_order(template_df=template_df) for _ in range(count)]
        return {"status": "success", "count": len(orders), "orders": orders}
    except Exception as e:
        print(f"Direct live order injection error: {e}", flush=True)
        return None


# ============================================================
# INITIALIZE FILTER DATA
# ============================================================

filter_meta = get_filter_options()

regions_list = filter_meta.get("regions", [])
categories_list = filter_meta.get("categories", [])
channels_list = filter_meta.get("channels", [])

try:
    min_date_val = datetime.strptime(filter_meta.get("min_date", "2023-08-07"), "%Y-%m-%d").date()
except Exception:
    min_date_val = date(2023, 8, 7)

try:
    max_date_val = datetime.strptime(filter_meta.get("max_date", "2026-08-16"), "%Y-%m-%d").date()
except Exception:
    max_date_val = date.today()

max_date_val = max(date.today(), max_date_val)


# ============================================================
# SIDEBAR CONTROLS
# ============================================================

with st.sidebar:
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
            <div style="background:#2563eb; color:white; padding:8px; border-radius:10px; display:flex;">
                {ICONS['layers']}
            </div>
            <div>
                <h3 style="margin:0; font-size:1.15rem; font-weight:800;">Executive Controls</h3>
                <span style="font-size:0.78rem; color:#64748b;">Enterprise Live Stream</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    live_monitoring = st.toggle("Live Stream Active", value=True)

    refresh_speed = st.select_slider(
        "Stream Polling Rate",
        options=[2, 3, 5, 10],
        value=3,
        format_func=lambda x: f"{x}s interval"
    )

    auto_sync_live = st.checkbox(
        "Auto-sync Live Orders",
        value=True,
        help="Continuously incorporate newest incoming live orders into real-time metrics"
    )

    # Interactive Demo Feature for Recruiters
    if st.button("⚡ Inject Test Live Order", help="Generates an immediate order directly into the database to demo live sync"):
        res = trigger_live_order_api(count=1)
        if res and res.get("status") == "success":
            st.toast("⚡ Live Order injected! Watch KPIs and ticker update.", icon="🚀")

    st.divider()

    st.markdown(f"**{ICONS['calendar']} Reporting Period**", unsafe_allow_html=True)
    selected_dates = st.date_input(
        "Date Range",
        value=(min_date_val, max_date_val),
        min_value=min_date_val,
        max_value=max_date_val + timedelta(days=365),
        label_visibility="collapsed"
    )

    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date = selected_dates[0]
        end_date = selected_dates[1]
    else:
        start_date = min_date_val
        end_date = max_date_val

    # Multi-select Segment Filters
    selected_regions = st.multiselect("Regions", regions_list, default=regions_list)
    selected_categories = st.multiselect("Categories", categories_list, default=categories_list)
    selected_channels = st.multiselect("Channels", channels_list, default=channels_list)

    st.divider()

    with st.expander("🔗 Backend Engine Settings", expanded=False):
        api_input = st.text_input(
            "FastAPI Server URL",
            value=st.session_state.get("api_url", default_api_url),
            help="For local: http://127.0.0.1:8000. For cloud: enter your deployed Render URL."
        )
        if api_input != st.session_state.get("api_url"):
            st.session_state["api_url"] = api_input.rstrip("/")
            st.rerun()

    st.markdown(
        f"""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px; font-size:0.78rem; color:#64748b;">
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <span>Engine:</span> <strong style="color:#0f172a;">FastAPI + SQLite WAL</strong>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span>Stream:</span> <strong style="color:#10b981;">Auto-Ingestion Active</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# Common filter parameters
filter_kwargs = {
    "start_date": start_date,
    "end_date": None if auto_sync_live else end_date,
    "regions": selected_regions if len(selected_regions) < len(regions_list) else None,
    "categories": selected_categories if len(selected_categories) < len(categories_list) else None,
    "channels": selected_channels if len(selected_channels) < len(channels_list) else None,
}


# ============================================================
# PERSISTENT BRAND HEADER (Rendered Once, No Flicker)
# ============================================================

st.markdown(
    f"""
    <div class="brand-container">
        <div class="brand-title-wrap">
            <div class="brand-logo-badge">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="20" x2="18" y2="10"></line>
                    <line x1="12" y1="20" x2="12" y2="4"></line>
                    <line x1="6" y1="20" x2="6" y2="14"></line>
                </svg>
            </div>
            <div>
                <h1 class="brand-title">AI KPI Monitor</h1>
                <p class="brand-subtitle">Executive Sales Intelligence & Real-Time Operational Risk Radar</p>
            </div>
        </div>
        <div>
            {f'<div class="live-status-pill"><div class="live-pulse-dot"></div><span>LIVE STREAM • {refresh_speed}s</span></div>' if live_monitoring else '<div class="live-status-pill" style="background:#f1f5f9; color:#475569; border-color:#cbd5e1;"><span>PAUSED</span></div>'}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 1. LIVE EXECUTIVE KPIs & TICKER FRAGMENT (Updates every 2-3s smoothly)
# ============================================================

@st.fragment(run_every=refresh_speed if live_monitoring else None)
def render_live_kpi_section():
    summary = get_dashboard_summary(**filter_kwargs)
    if not summary or summary.get("status") != "success":
        st.warning(f"⚠️ Synchronizing with backend API stream ({API_BASE_URL})...")
        return

    kpis = summary.get("kpis", {})
    total_monitored = summary.get("total_monitored", 0)
    engine_name = summary.get("engine", "Operational (Online)")
    revenue = kpis.get("revenue", 0.0)
    orders = kpis.get("orders", 0)
    customers = kpis.get("customers", 0)
    aov = kpis.get("average_order_value", 0.0)
    profit = kpis.get("profit", 0.0)
    margin = kpis.get("profit_margin", 0.0)

    # Overview row
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(
            f"""
            <div class="sys-card">
                <div class="sys-icon-box">{ICONS['server']}</div>
                <div>
                    <div class="sys-label">System Health</div>
                    <div class="sys-val" style="color:#059669; font-size:0.96rem;">{engine_name}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with s2:
        st.markdown(
            f"""
            <div class="sys-card">
                <div class="sys-icon-box">{ICONS['database']}</div>
                <div>
                    <div class="sys-label">Records Monitored</div>
                    <div class="sys-val">{total_monitored:,}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with s3:
        period_str = f"{start_date} → {'Live (Today)' if auto_sync_live else end_date}"
        st.markdown(
            f"""
            <div class="sys-card">
                <div class="sys-icon-box">{ICONS['calendar']}</div>
                <div>
                    <div class="sys-label">Reporting Window</div>
                    <div class="sys-val" style="font-size:0.96rem;">{period_str}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 6 Executive KPI Metric Cards
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-top: 3px solid #10b981;">
                <div class="kpi-top-row">
                    <span class="kpi-label">Gross Revenue</span>
                    <div class="kpi-icon-box" style="background:#ecfdf5;">{ICONS['revenue']}</div>
                </div>
                <div class="kpi-metric-val">{money(revenue)}</div>
                <div class="kpi-footer-sub">
                    <span style="color:#059669; font-weight:600;">● Live Streamed</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k2:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-top: 3px solid #2563eb;">
                <div class="kpi-top-row">
                    <span class="kpi-label">Total Orders</span>
                    <div class="kpi-icon-box" style="background:#eff6ff;">{ICONS['orders']}</div>
                </div>
                <div class="kpi-metric-val">{orders:,}</div>
                <div class="kpi-footer-sub">
                    <span style="color:#2563eb; font-weight:600;">● Real-time Transactions</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k3:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-top: 3px solid #6366f1;">
                <div class="kpi-top-row">
                    <span class="kpi-label">Active Customers</span>
                    <div class="kpi-icon-box" style="background:#eef2ff;">{ICONS['customers']}</div>
                </div>
                <div class="kpi-metric-val">{customers:,}</div>
                <div class="kpi-footer-sub">
                    <span style="color:#6366f1; font-weight:600;">● Unique Buyers</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    k4, k5, k6 = st.columns(3)
    with k4:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-top: 3px solid #8b5cf6;">
                <div class="kpi-top-row">
                    <span class="kpi-label">Average Order Value</span>
                    <div class="kpi-icon-box" style="background:#f5f3ff;">{ICONS['aov']}</div>
                </div>
                <div class="kpi-metric-val">{money(aov)}</div>
                <div class="kpi-footer-sub">
                    <span>Revenue per order</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k5:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-top: 3px solid #059669;">
                <div class="kpi-top-row">
                    <span class="kpi-label">Net Profit</span>
                    <div class="kpi-icon-box" style="background:#ecfdf5;">{ICONS['profit']}</div>
                </div>
                <div class="kpi-metric-val">{money(profit)}</div>
                <div class="kpi-footer-sub">
                    <span style="color:#059669; font-weight:600;">● Bottom-line yield</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k6:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-top: 3px solid #0d9488;">
                <div class="kpi-top-row">
                    <span class="kpi-label">Profit Margin</span>
                    <div class="kpi-icon-box" style="background:#f0fdfa;">{ICONS['margin']}</div>
                </div>
                <div class="kpi-metric-val">{margin:.1f}%</div>
                <div class="kpi-footer-sub">
                    <span>Margin efficiency</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Live Transaction Ribbon Ticker
    latest = get_latest_order()
    if latest:
        latest_id = latest.get("Order_ID", "N/A")
        latest_date = latest.get("Order_Date", "N/A")
        latest_customer = latest.get("Customer_Name", "N/A")
        latest_product = latest.get("Product", "N/A")
        latest_revenue = safe_float(latest.get("Revenue", 0))

        st.markdown(
            f"""
            <div class="tx-ribbon">
                <div class="tx-left">
                    <div style="display:flex; align-items:center; gap:6px;">
                        {ICONS['zap']}
                        <span class="tx-pill">LATEST TRANSACTION</span>
                    </div>
                    <span class="tx-meta">
                        <strong>Order #{latest_id}</strong> &nbsp;•&nbsp; 
                        <span>{latest_date}</span> &nbsp;•&nbsp; 
                        <span>{latest_customer}</span> &nbsp;•&nbsp; 
                        <span style="color:#4f46e5; font-weight:600;">{latest_product}</span>
                    </span>
                </div>
                <div class="tx-amount">{money(latest_revenue)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


render_live_kpi_section()


# ============================================================
# 2. PERFORMANCE TRAJECTORY & MARKET CHARTS FRAGMENT (15s cadence, No flicker)
# ============================================================

@st.fragment(run_every=15 if live_monitoring else None)
def render_charts_section():
    summary = get_dashboard_summary(**filter_kwargs)
    if not summary:
        return

    st.markdown(
        f"""
        <div class="section-header">
            <span style="display:flex; align-items:center;">{ICONS['chart']}</span>
            <h2 class="section-title">Revenue & Profit Trajectory</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    monthly_data = pd.DataFrame(summary.get("monthly_trend", []))
    if not monthly_data.empty:
        chart1, chart2 = st.columns(2)
        with chart1:
            fig_rev = px.line(
                monthly_data,
                x="Month",
                y="Revenue",
                markers=True,
                title="Monthly Revenue Trend",
                color_discrete_sequence=["#2563EB"]
            )
            fig_rev.update_layout(
                template="plotly_white",
                margin=dict(l=10, r=10, t=36, b=10),
                height=280,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
                font=dict(family="Plus Jakarta Sans, sans-serif")
            )
            st.plotly_chart(fig_rev, use_container_width=True, key="live_rev_line_chart")

        with chart2:
            fig_prof = px.bar(
                monthly_data,
                x="Month",
                y="Profit",
                title="Monthly Profit Trend",
                color_discrete_sequence=["#10B981"]
            )
            fig_prof.update_layout(
                template="plotly_white",
                margin=dict(l=10, r=10, t=36, b=10),
                height=280,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
                font=dict(family="Plus Jakarta Sans, sans-serif")
            )
            st.plotly_chart(fig_prof, use_container_width=True, key="live_prof_bar_chart")

    # Territory & Channel Breakdown
    st.markdown(
        f"""
        <div class="section-header">
            <span style="display:flex; align-items:center;">{ICONS['pie']}</span>
            <h2 class="section-title">Market & Channel Breakdown</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    b1, b2 = st.columns(2)
    region_data = pd.DataFrame(summary.get("region_breakdown", []))
    category_data = pd.DataFrame(summary.get("category_breakdown", []))
    channel_data = pd.DataFrame(summary.get("channel_breakdown", []))

    with b1:
        if not region_data.empty:
            fig_region = px.bar(
                region_data,
                x="Revenue",
                y="Region",
                orientation="h",
                title="Revenue by Territory",
                color_discrete_sequence=["#3B82F6"]
            )
            fig_region.update_layout(
                template="plotly_white",
                margin=dict(l=10, r=10, t=36, b=10),
                height=270,
                xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
                yaxis=dict(autorange="reversed"),
                font=dict(family="Plus Jakarta Sans, sans-serif")
            )
            st.plotly_chart(fig_region, use_container_width=True, key="live_region_bar")

    with b2:
        if not category_data.empty:
            fig_cat = px.bar(
                category_data,
                x="Revenue",
                y="Category",
                orientation="h",
                title="Revenue by Category",
                color_discrete_sequence=["#8B5CF6"]
            )
            fig_cat.update_layout(
                template="plotly_white",
                margin=dict(l=10, r=10, t=36, b=10),
                height=270,
                xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
                yaxis=dict(autorange="reversed"),
                font=dict(family="Plus Jakarta Sans, sans-serif")
            )
            st.plotly_chart(fig_cat, use_container_width=True, key="live_category_bar")

    if not channel_data.empty:
        fig_chan = px.pie(
            channel_data,
            values="Revenue",
            names="Sales_Channel",
            hole=0.55,
            title="Distribution by Sales Channel",
            color_discrete_sequence=["#0284C7", "#F59E0B"]
        )
        fig_chan.update_layout(
            template="plotly_white",
            margin=dict(l=10, r=10, t=36, b=10),
            height=250,
            font=dict(family="Plus Jakarta Sans, sans-serif")
        )
        st.plotly_chart(fig_chan, use_container_width=True, key="live_channel_donut")


render_charts_section()


# ============================================================
# 3. OPERATIONAL RISK & ANOMALY RADAR FRAGMENT (Updates in real-time)
# ============================================================

@st.fragment(run_every=refresh_speed if live_monitoring else None)
def render_risk_radar_section():
    st.markdown(
        f"""
        <div class="section-header">
            <span style="display:flex; align-items:center;">{ICONS['shield_alert']}</span>
            <h2 class="section-title">Operational Risk & Anomaly Radar</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    anomaly_resp = get_anomalies(limit=10)
    anomalies_list = anomaly_resp.get("data", [])
    critical = anomaly_resp.get("critical", 0)
    high = anomaly_resp.get("high", 0)
    medium = anomaly_resp.get("medium", 0)
    active_alerts = len(anomalies_list)

    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-top: 3px solid #e11d48; padding:12px 16px;">
                <div class="kpi-label" style="color:#e11d48;">Critical Alerts</div>
                <div class="kpi-metric-val" style="color:#e11d48; font-size:1.6rem;">{critical:,}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with a2:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-top: 3px solid #f97316; padding:12px 16px;">
                <div class="kpi-label" style="color:#f97316;">High Severity</div>
                <div class="kpi-metric-val" style="color:#f97316; font-size:1.6rem;">{high:,}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with a3:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-top: 3px solid #ca8a04; padding:12px 16px;">
                <div class="kpi-label" style="color:#ca8a04;">Medium Severity</div>
                <div class="kpi-metric-val" style="color:#ca8a04; font-size:1.6rem;">{medium:,}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with a4:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-top: 3px solid #2563eb; padding:12px 16px;">
                <div class="kpi-label" style="color:#2563eb;">Total Active</div>
                <div class="kpi-metric-val" style="font-size:1.6rem;">{active_alerts:,}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if anomalies_list:
        st.markdown("<p style='font-size:0.86rem; font-weight:600; color:#475569; margin:6px 0 6px 0;'>Live Detected Anomaly Stream</p>", unsafe_allow_html=True)
        for item in anomalies_list[:4]:
            sev = str(item.get("Severity", "Medium")).upper()
            order_id = item.get("Order_ID", "N/A")
            customer = item.get("Customer_Name", "Unknown")
            product = item.get("Product", "Unknown")
            region = item.get("Region", "Unknown")
            revenue_val = safe_float(item.get("Revenue", 0))
            reason = item.get("Anomaly_Reason", "Unusual transaction pattern detected")

            if sev == "CRITICAL":
                card_cls = "alert-critical"
                badge_html = '<span class="alert-badge-crit">CRITICAL</span>'
            elif sev == "HIGH":
                card_cls = "alert-high"
                badge_html = '<span class="alert-badge-high">HIGH</span>'
            else:
                card_cls = "alert-medium"
                badge_html = '<span class="alert-badge-med">MEDIUM</span>'

            st.markdown(
                f"""
                <div class="alert-card {card_cls}">
                    <div class="alert-top">
                        <span style="font-weight:700; font-size:0.88rem;">Order #{order_id} &nbsp;•&nbsp; {customer} &nbsp;•&nbsp; {product} ({region})</span>
                        {badge_html}
                    </div>
                    <div class="alert-msg">
                        Revenue Impact: <strong>{money(revenue_val)}</strong> &nbsp;|&nbsp; <strong>Trigger:</strong> {reason}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.success("✅ Zero active anomalies detected in current stream window.")


render_risk_radar_section()


# ============================================================
# 4. 🧠 EXECUTIVE AI BUSINESS INSIGHTS FRAGMENT (20s cycle)
# ============================================================

@st.fragment(run_every=20 if live_monitoring else None)
def render_executive_insights_section():
    st.markdown(
        f"""
        <div class="section-header">
            <span style="display:flex; align-items:center;">{ICONS['sparkles']}</span>
            <h2 class="section-title">Executive AI Business Intelligence</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    ai_data = get_ai_insights(**filter_kwargs)
    if ai_data:
        alert_title = ai_data.get("alert_title", "⚡ Executive Business Intelligence Radar")
        severity = ai_data.get("severity", "Healthy")
        exec_summary = ai_data.get("executive_summary", "")
        drivers = ai_data.get("key_drivers", [])
        risk_text = ai_data.get("risk_assessment", "")
        actions = ai_data.get("recommended_actions", [])

        if severity == "Warning":
            badge_class = "ai-badge-alert"
        elif severity == "Positive":
            badge_class = "ai-badge-growth"
        else:
            badge_class = "ai-badge-radar"

        st.markdown(
            f"""
            <div class="ai-insights-box">
                <div class="ai-header-row">
                    <div class="ai-title-wrap">
                        <span class="{badge_class}">{alert_title}</span>
                    </div>
                    <span style="font-size:0.78rem; font-weight:600; color:#64748b;">
                        ⚡ Real-Time Intelligence & Anomaly Synthesis
                    </span>
                </div>
                <div class="ai-narrative-card">
                    <strong>Executive Briefing:</strong> {exec_summary}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 3 Key Business Drivers
        if drivers:
            st.markdown("<p style='font-size:0.88rem; font-weight:700; color:#334155; margin:4px 0 8px 0;'>📊 Key Performance Drivers</p>", unsafe_allow_html=True)
            d_cols = st.columns(len(drivers[:3]))
            icons_list = [ICONS['chart'], ICONS['pie'], ICONS['activity']]
            for i, driver_text in enumerate(drivers[:3]):
                with d_cols[i]:
                    st.markdown(
                        f"""
                        <div class="ai-driver-card">
                            <div style="margin-bottom:6px;">{icons_list[i % len(icons_list)]}</div>
                            <div>{driver_text}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        # Recommended Strategic Actions & Operational Risk
        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        act_col, risk_col = st.columns([3, 2])

        with act_col:
            st.markdown("<p style='font-size:0.88rem; font-weight:700; color:#15803d; margin-bottom:6px;'>🎯 Recommended Strategic Actions</p>", unsafe_allow_html=True)
            for act in actions:
                st.markdown(
                    f"""
                    <div class="ai-action-card">
                        • {act}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with risk_col:
            st.markdown("<p style='font-size:0.88rem; font-weight:700; color:#e11d48; margin-bottom:6px;'>🛡️ Operational Risk Radar</p>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="ai-driver-card" style="border-left: 3px solid #e11d48; background:#fff1f2;">
                    <div style="font-weight:700; color:#9f1239; margin-bottom:4px;">Governance & Integrity:</div>
                    <div style="color:#881337; font-size:0.84rem;">{risk_text}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("AI Insights synthesis is synchronizing with live data stream...")


render_executive_insights_section()


# ============================================================
# 5. TOP PRODUCTS & LIVE INGESTION TABLES FRAGMENT (Real-time update)
# ============================================================

@st.fragment(run_every=refresh_speed if live_monitoring else None)
def render_tables_section():
    t1, t2 = st.columns([1, 2])

    with t1:
        st.markdown(
            f"""
            <div class="section-header">
                <span style="display:flex; align-items:center;">{ICONS['orders']}</span>
                <h3 class="section-title" style="font-size:1.05rem;">Top Products</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        summary = get_dashboard_summary(**filter_kwargs)
        top_products_data = summary.get("top_products", []) if summary else []
        if top_products_data:
            top_df = pd.DataFrame(top_products_data)
            if "Revenue" in top_df.columns:
                top_df["Revenue"] = top_df["Revenue"].apply(money)
            st.dataframe(top_df, use_container_width=True, hide_index=True, height=280)

    with t2:
        st.markdown(
            f"""
            <div class="section-header">
                <span style="display:flex; align-items:center;">{ICONS['zap']}</span>
                <h3 class="section-title" style="font-size:1.05rem;">Live Ingestion Stream</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        latest_orders_df = get_latest_orders(limit=10)
        if not latest_orders_df.empty:
            display_columns = [
                "Order_ID", "Order_Date", "Customer_Name", "Product",
                "Quantity", "Revenue", "Profit", "Sales_Channel", "Anomaly"
            ]
            available_columns = [c for c in display_columns if c in latest_orders_df.columns]
            display_df = latest_orders_df[available_columns].copy()

            if "Revenue" in display_df.columns:
                display_df["Revenue"] = display_df["Revenue"].apply(money)
            if "Profit" in display_df.columns:
                display_df["Profit"] = display_df["Profit"].apply(money)

            st.dataframe(display_df, use_container_width=True, hide_index=True, height=280)


render_tables_section()


# ============================================================
# PERSISTENT FOOTER
# ============================================================

st.divider()
st.markdown(
    f"""
    <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.78rem; color:#94a3b8;">
        <span>AI KPI Monitor • Executive Sales Intelligence</span>
        <span>Last Synchronized: <strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong></span>
        <span>Polling Cadence: <strong>{refresh_speed}s</strong></span>
    </div>
    """,
    unsafe_allow_html=True
)