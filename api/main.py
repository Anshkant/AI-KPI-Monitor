from typing import Optional, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
import sqlite3
import os
import sys
import statistics

# ============================================================
# PROJECT PATHS & IMPORTS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import asyncio
from database.init_db import ensure_database, is_database_initialized, DB_PATH
from src.live_data_generator import generate_single_order, get_template_df

# ============================================================
# LIVE STREAM GENERATOR BACKGROUND WORKER STATE
# ============================================================

live_stream_state = {
    "enabled": True,
    "interval": 3.0,
    "generated_count": 0,
    "last_order": None,
    "task": None
}


async def background_order_generator():
    """Background async worker that continuously streams live orders directly into sales.db."""
    print("[Live Stream Worker] Background live order generator started (Production-grade streaming).")
    try:
        template_df = get_template_df()
    except Exception as err:
        print(f"[Live Stream Worker Warning] Could not load template data: {err}")
        template_df = None

    while True:
        try:
            if live_stream_state["enabled"] and template_df is not None:
                order = generate_single_order(template_df=template_df)
                live_stream_state["generated_count"] += 1
                live_stream_state["last_order"] = order
        except Exception as e:
            print(f"[Live Stream Worker Error] {e}", file=sys.stderr)

        await asyncio.sleep(live_stream_state["interval"])


# ============================================================
# FASTAPI LIFESPAN & APP
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Auto-initialize database on application startup if missing
    print("[API Startup] Verifying database integrity...")
    ensure_database(verbose=True)

    # 2. Automatically launch background live order streamer
    worker_task = asyncio.create_task(background_order_generator())
    live_stream_state["task"] = worker_task

    yield

    # Clean shutdown of generator
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    print("[API Shutdown] Background live generator stopped.")


app = FastAPI(
    title="AI KPI Monitor API",
    description="Real time sales monitoring API",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    if not is_database_initialized(DB_PATH):
        ensure_database(verbose=True)

    conn = sqlite3.connect(
        DB_PATH,
        timeout=15
    )
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn


# ============================================================
# CLEAN DATABASE VALUES
# ============================================================

def clean_value(value):

    if isinstance(value, bytes):

        try:
            return value.decode("utf-8")

        except UnicodeDecodeError:

            return value.decode(
                "cp1252",
                errors="replace"
            )

    return value


# ============================================================
# CONVERT ROWS TO JSON SAFE DICTS
# ============================================================

def rows_to_dicts(cursor, rows):

    columns = [
        description[0]
        for description in cursor.description
    ]

    return [
        {
            column: clean_value(value)
            for column, value in zip(columns, row)
        }
        for row in rows
    ]


# ============================================================
# ANOMALY SEVERITY + REASON
# ============================================================

def calculate_anomaly_details(
    revenue,
    quantity,
    revenue_mean,
    revenue_std,
    quantity_mean,
    quantity_std
):

    reasons = []

    # --------------------------------------------------------
    # Revenue anomaly
    # --------------------------------------------------------

    revenue_score = 0

    if revenue_std > 0:

        revenue_score = abs(
            revenue - revenue_mean
        ) / revenue_std

    if revenue_score >= 4:

        reasons.append(
            "Extremely unusual revenue value"
        )

    elif revenue_score >= 3:

        reasons.append(
            "Unusual revenue value"
        )

    # --------------------------------------------------------
    # Quantity anomaly
    # --------------------------------------------------------

    quantity_score = 0

    if quantity_std > 0:

        quantity_score = abs(
            quantity - quantity_mean
        ) / quantity_std

    if quantity_score >= 4:

        reasons.append(
            "Extremely unusual order quantity"
        )

    elif quantity_score >= 3:

        reasons.append(
            "Unusual order quantity"
        )

    # --------------------------------------------------------
    # Negative revenue
    # --------------------------------------------------------

    if revenue < 0:

        reasons.append(
            "Negative revenue transaction"
        )

    # --------------------------------------------------------
    # Severity
    # --------------------------------------------------------

    max_score = max(
        revenue_score,
        quantity_score
    )

    if max_score >= 4:

        severity = "Critical"

    elif max_score >= 3:

        severity = "High"

    else:

        severity = "Medium"

    # --------------------------------------------------------
    # Fallback reason
    # --------------------------------------------------------

    if not reasons:

        reasons.append(
            "Unusual transaction pattern detected"
        )

    reason = " + ".join(reasons)

    return severity, reason


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "status": "success",
        "message": "AI KPI Monitor API is running"
    }


# ============================================================
# SQL FILTER BUILDER HELPER
# ============================================================

def build_where_clause(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    regions: Optional[str] = None,
    categories: Optional[str] = None,
    channels: Optional[str] = None
):
    clauses = []
    params = []

    if start_date:
        clauses.append("substr(Order_Date, 1, 10) >= ?")
        params.append(str(start_date))

    if end_date:
        clauses.append("substr(Order_Date, 1, 10) <= ?")
        params.append(str(end_date))

    if regions:
        region_list = [r.strip() for r in regions.split(",") if r.strip()]
        if region_list:
            placeholders = ",".join(["?"] * len(region_list))
            clauses.append(f"Region IN ({placeholders})")
            params.extend(region_list)

    if categories:
        cat_list = [c.strip() for c in categories.split(",") if c.strip()]
        if cat_list:
            placeholders = ",".join(["?"] * len(cat_list))
            clauses.append(f"Category IN ({placeholders})")
            params.extend(cat_list)

    if channels:
        chan_list = [ch.strip() for ch in channels.split(",") if ch.strip()]
        if chan_list:
            placeholders = ",".join(["?"] * len(chan_list))
            clauses.append(f"Sales_Channel IN ({placeholders})")
            params.extend(chan_list)

    where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    return where_sql, params


# ============================================================
# GET FILTER OPTIONS
# ============================================================

@app.get("/sales/filter-options")
def get_filter_options():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT Region FROM sales WHERE Region IS NOT NULL ORDER BY Region")
        regions = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT Category FROM sales WHERE Category IS NOT NULL ORDER BY Category")
        categories = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT Sales_Channel FROM sales WHERE Sales_Channel IS NOT NULL ORDER BY Sales_Channel")
        channels = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT MIN(substr(Order_Date, 1, 10)), MAX(substr(Order_Date, 1, 10)), COUNT(*) FROM sales")
        min_date, max_date, total_count = cursor.fetchone()

        return {
            "status": "success",
            "regions": regions,
            "categories": categories,
            "channels": channels,
            "min_date": min_date or "",
            "max_date": max_date or "",
            "total_records": total_count or 0
        }
    finally:
        conn.close()


# ============================================================
# FAST DASHBOARD SUMMARY (Pre-aggregated SQL for ultra-smooth UI)
# ============================================================

@app.get("/sales/dashboard-summary")
def get_dashboard_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    regions: Optional[str] = None,
    categories: Optional[str] = None,
    channels: Optional[str] = None
):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Total in DB
        cursor.execute("SELECT COUNT(*), MIN(substr(Order_Date, 1, 10)), MAX(substr(Order_Date, 1, 10)) FROM sales")
        total_monitored, min_db_date, max_db_date = cursor.fetchone()

        where_sql, params = build_where_clause(start_date, end_date, regions, categories, channels)

        # Filtered KPIs
        cursor.execute(
            f"""
            SELECT
                COALESCE(SUM(Revenue), 0),
                COUNT(*),
                COUNT(DISTINCT Customer_ID),
                COALESCE(AVG(Revenue), 0),
                COALESCE(SUM(Profit), 0)
            FROM sales
            {where_sql}
            """,
            params
        )
        rev, orders_count, cust_count, aov, prof = cursor.fetchone()
        margin = (prof / rev * 100) if (rev and rev != 0) else 0.0

        # Monthly Trend (Revenue & Profit)
        cursor.execute(
            f"""
            SELECT
                strftime('%Y-%m', Order_Date) AS Month,
                COALESCE(SUM(Revenue), 0) AS Revenue,
                COALESCE(SUM(Profit), 0) AS Profit
            FROM sales
            {where_sql}
            GROUP BY Month
            ORDER BY Month ASC
            """,
            params
        )
        monthly_trend = [
            {"Month": row[0], "Revenue": float(row[1]), "Profit": float(row[2])}
            for row in cursor.fetchall() if row[0]
        ]

        # Region Breakdown
        cursor.execute(
            f"""
            SELECT
                Region,
                COALESCE(SUM(Revenue), 0) AS Revenue
            FROM sales
            {where_sql}
            GROUP BY Region
            ORDER BY Revenue DESC
            """,
            params
        )
        region_breakdown = [
            {"Region": row[0], "Revenue": float(row[1])}
            for row in cursor.fetchall() if row[0]
        ]

        # Category Breakdown
        cursor.execute(
            f"""
            SELECT
                Category,
                COALESCE(SUM(Revenue), 0) AS Revenue
            FROM sales
            {where_sql}
            GROUP BY Category
            ORDER BY Revenue DESC
            """,
            params
        )
        category_breakdown = [
            {"Category": row[0], "Revenue": float(row[1])}
            for row in cursor.fetchall() if row[0]
        ]

        # Sales Channel Breakdown
        cursor.execute(
            f"""
            SELECT
                Sales_Channel,
                COALESCE(SUM(Revenue), 0) AS Revenue
            FROM sales
            {where_sql}
            GROUP BY Sales_Channel
            ORDER BY Revenue DESC
            """,
            params
        )
        channel_breakdown = [
            {"Sales_Channel": row[0], "Revenue": float(row[1])}
            for row in cursor.fetchall() if row[0]
        ]

        # Top Products
        cursor.execute(
            f"""
            SELECT
                Product,
                COALESCE(SUM(Revenue), 0) AS Revenue
            FROM sales
            {where_sql}
            GROUP BY Product
            ORDER BY Revenue DESC
            LIMIT 10
            """,
            params
        )
        top_products = [
            {"Product": row[0], "Revenue": float(row[1])}
            for row in cursor.fetchall() if row[0]
        ]

        return {
            "status": "success",
            "total_monitored": total_monitored or 0,
            "min_date": min_db_date or "",
            "max_date": max_db_date or "",
            "kpis": {
                "revenue": float(rev or 0),
                "orders": int(orders_count or 0),
                "customers": int(cust_count or 0),
                "average_order_value": float(aov or 0),
                "profit": float(prof or 0),
                "profit_margin": round(float(margin), 2)
            },
            "monthly_trend": monthly_trend,
            "region_breakdown": region_breakdown,
            "category_breakdown": category_breakdown,
            "channel_breakdown": channel_breakdown,
            "top_products": top_products
        }
    finally:
        conn.close()


# ============================================================
# GET SALES
# ============================================================


@app.get("/sales")
def get_sales(limit: int = 100):

    limit = max(
        1,
        min(limit, 100000)
    )

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM sales
            LIMIT ?
            """,
            (limit,)
        )

        rows = cursor.fetchall()

        data = rows_to_dicts(
            cursor,
            rows
        )

        return {
            "count": len(data),
            "data": data
        }

    finally:

        conn.close()


# ============================================================
# GET LATEST SALES
# ============================================================

@app.get("/sales/latest")
def get_latest_sales(limit: int = 10):

    limit = max(
        1,
        min(limit, 100)
    )

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM sales
            ORDER BY Order_ID DESC
            LIMIT ?
            """,
            (limit,)
        )

        rows = cursor.fetchall()

        data = rows_to_dicts(
            cursor,
            rows
        )

        return {
            "count": len(data),
            "data": data
        }

    finally:

        conn.close()


# ============================================================
# GET KPIs
# ============================================================

@app.get("/kpis")
def get_kpis():

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                COALESCE(SUM(Revenue), 0),
                COUNT(*),
                COUNT(DISTINCT Customer_ID),
                COALESCE(AVG(Revenue), 0),
                COALESCE(SUM(Profit), 0)
            FROM sales
            """
        )

        revenue, orders, customers, aov, profit = (
            cursor.fetchone()
        )

        return {
            "revenue": revenue or 0,
            "orders": orders or 0,
            "customers": customers or 0,
            "average_order_value": aov or 0,
            "profit": profit or 0
        }

    finally:

        conn.close()


# ============================================================
# GET LATEST ORDER ONLY
# ============================================================

@app.get("/sales/latest-one")
def get_latest_order():

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM sales
            ORDER BY Order_ID DESC
            LIMIT 1
            """
        )

        row = cursor.fetchone()

        if row is None:

            return {
                "status": "empty",
                "data": None
            }

        data = rows_to_dicts(
            cursor,
            [row]
        )[0]

        return {
            "status": "success",
            "data": data
        }

    finally:

        conn.close()


# ============================================================
# GET LATEST ANOMALIES
# ============================================================

@app.get("/anomalies/latest")
def get_latest_anomalies(
    limit: int = 10
):

    limit = max(
        1,
        min(limit, 100)
    )

    conn = get_connection()

    try:

        cursor = conn.cursor()

        # ----------------------------------------------------
        # Get statistical baseline
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                Revenue,
                Quantity
            FROM sales
            WHERE Revenue IS NOT NULL
            """
        )

        baseline_rows = cursor.fetchall()

        revenues = []
        quantities = []

        for revenue, quantity in baseline_rows:

            if isinstance(revenue, (int, float)):

                revenues.append(
                    float(revenue)
                )

            if isinstance(quantity, (int, float)):

                quantities.append(
                    float(quantity)
                )

        # ----------------------------------------------------
        # Calculate baseline statistics
        # ----------------------------------------------------

        revenue_mean = (
            statistics.mean(revenues)
            if revenues
            else 0
        )

        revenue_std = (
            statistics.stdev(revenues)
            if len(revenues) > 1
            else 0
        )

        quantity_mean = (
            statistics.mean(quantities)
            if quantities
            else 0
        )

        quantity_std = (
            statistics.stdev(quantities)
            if len(quantities) > 1
            else 0
        )

        # ----------------------------------------------------
        # Get anomalous orders
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM sales
            WHERE Anomaly = 'Anomaly'
            ORDER BY Order_ID DESC
            LIMIT ?
            """,
            (limit,)
        )

        rows = cursor.fetchall()

        data = rows_to_dicts(
            cursor,
            rows
        )

        # ----------------------------------------------------
        # Add severity + reason
        # ----------------------------------------------------

        enhanced_data = []

        for item in data:

            revenue = item.get(
                "Revenue",
                0
            )

            quantity = item.get(
                "Quantity",
                0
            )

            try:

                revenue = float(
                    revenue
                )

            except (
                TypeError,
                ValueError
            ):

                revenue = 0

            try:

                quantity = float(
                    quantity
                )

            except (
                TypeError,
                ValueError
            ):

                quantity = 0

            severity, reason = (
                calculate_anomaly_details(
                    revenue,
                    quantity,
                    revenue_mean,
                    revenue_std,
                    quantity_mean,
                    quantity_std
                )
            )

            item["Severity"] = severity

            item["Anomaly_Reason"] = reason

            enhanced_data.append(item)

        # ----------------------------------------------------
        # Severity summary
        # ----------------------------------------------------

        critical_count = sum(
            1
            for item in enhanced_data
            if item["Severity"] == "Critical"
        )

        high_count = sum(
            1
            for item in enhanced_data
            if item["Severity"] == "High"
        )

        medium_count = sum(
            1
            for item in enhanced_data
            if item["Severity"] == "Medium"
        )

        return {
            "count": len(enhanced_data),

            "critical": critical_count,

            "high": high_count,

            "medium": medium_count,

            "data": enhanced_data
        }

    finally:

        conn.close()


# ============================================================
# GET ANOMALY SUMMARY
# ============================================================

@app.get("/anomalies/summary")
def get_anomaly_summary():

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM sales
            WHERE Anomaly = 'Anomaly'
            """
        )

        anomaly_count = (
            cursor.fetchone()[0]
            or 0
        )

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM sales
            WHERE Anomaly = 'Normal'
            """
        )

        normal_count = (
            cursor.fetchone()[0]
            or 0
        )

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM sales
            """
        )

        total_count = (
            cursor.fetchone()[0]
            or 0
        )

        anomaly_rate = (
            anomaly_count / total_count * 100
            if total_count > 0
            else 0
        )

        return {

            "total_orders": total_count,

            "anomalies": anomaly_count,

            "normal_orders": normal_count,

            "anomaly_rate": round(
                anomaly_rate,
                2
            )

        }

    finally:

        conn.close()


# ============================================================
# GET AI EXECUTIVE BUSINESS INSIGHTS
# ============================================================

@app.get("/ai/executive-insights")
def get_ai_executive_insights(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    regions: Optional[str] = None,
    categories: Optional[str] = None,
    channels: Optional[str] = None,
    use_gemini: bool = False
):
    from src.ai_summary import generate_executive_insights
    import pandas as pd

    conn = get_connection()
    try:
        where_sql, params = build_where_clause(start_date, end_date, regions, categories, channels)
        query = f"""
            SELECT
                Order_ID,
                Order_Date,
                Customer_ID,
                Region,
                Category,
                Product,
                Quantity,
                Revenue,
                Cost,
                Profit,
                Returned,
                Sales_Channel,
                Anomaly
            FROM sales
            {where_sql}
            ORDER BY Order_Date ASC
        """
        df = pd.read_sql_query(query, conn, params=params)
        insights = generate_executive_insights(df=df, use_gemini=use_gemini)
        return {
            "status": "success",
            "insights": insights
        }
    finally:
        conn.close()


# ============================================================
# LIVE ORDER GENERATOR MANAGEMENT ENDPOINTS
# ============================================================

@app.get("/generator/status")
def get_generator_status():
    return {
        "status": "success",
        "active": live_stream_state["enabled"],
        "interval_seconds": live_stream_state["interval"],
        "total_generated": live_stream_state["generated_count"],
        "last_order": live_stream_state["last_order"]
    }


@app.post("/generator/toggle")
def toggle_generator(enabled: Optional[bool] = None, interval: Optional[float] = None):
    if enabled is not None:
        live_stream_state["enabled"] = enabled
    if interval is not None and interval >= 0.5:
        live_stream_state["interval"] = float(interval)
    return {
        "status": "success",
        "active": live_stream_state["enabled"],
        "interval_seconds": live_stream_state["interval"],
        "total_generated": live_stream_state["generated_count"]
    }


@app.post("/generator/trigger")
def trigger_orders(count: int = 1):
    count = max(1, min(count, 50))
    template_df = get_template_df()
    created = []
    for _ in range(count):
        order = generate_single_order(template_df=template_df)
        live_stream_state["generated_count"] += 1
        live_stream_state["last_order"] = order
        created.append(order)
    return {
        "status": "success",
        "count": len(created),
        "orders": created
    }