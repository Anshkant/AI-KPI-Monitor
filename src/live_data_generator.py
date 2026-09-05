import sqlite3
import pandas as pd
import random
import time
import os
import sys
from datetime import datetime

# Project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Fix Windows console UTF-8 output encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from database.init_db import ensure_database, find_source_data, is_database_initialized, DB_PATH

_cached_template_df = None


def get_template_df():
    """Loads and caches seed dataset as templates for generating realistic live orders."""
    global _cached_template_df
    if _cached_template_df is None:
        source_file = find_source_data()
        df = pd.read_csv(source_file)
        if "Order_Date" in df.columns:
            df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
        _cached_template_df = df
    return _cached_template_df


def get_db_connection():
    """Returns an active SQLite WAL-mode connection."""
    if not is_database_initialized(DB_PATH):
        ensure_database(verbose=False)
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn


def generate_single_order(conn=None, template_df=None) -> dict:
    """
    Generates and inserts a single realistic live sales order directly into sales.db.
    Returns the created order as a dictionary.
    """
    if template_df is None:
        template_df = get_template_df()

    should_close_conn = False
    if conn is None:
        conn = get_db_connection()
        should_close_conn = True

    try:
        # Select random existing order as template
        new_order = template_df.sample(1).iloc[0].copy()

        # Generate new Order ID
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(MAX(Order_ID), 100000) FROM sales")
            max_order_id = cursor.fetchone()[0]
            new_order["Order_ID"] = int(max_order_id) + 1
        except Exception:
            new_order["Order_ID"] = int(time.time())

        # Current timestamp
        new_order["Order_Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Realistic baseline parameters
        quantity = random.randint(1, 10)
        unit_price = float(random.randint(500, 25000))
        discount_pct = float(random.choice([0, 5, 10, 15, 20]))

        # 20% chance of anomaly for live detection radar
        is_anomaly = random.random() < 0.20
        if is_anomaly:
            anomaly_type = random.choice(["huge_qty", "heavy_discount", "high_rev", "negative"])
            if anomaly_type == "huge_qty":
                quantity = random.randint(35, 75)
                discount_pct = 5.0
            elif anomaly_type == "heavy_discount":
                discount_pct = 70.0
            elif anomaly_type == "high_rev":
                unit_price = unit_price * random.uniform(4.0, 8.0)
            elif anomaly_type == "negative":
                unit_price = -abs(unit_price)

            new_order["Anomaly"] = "Anomaly"
        else:
            new_order["Anomaly"] = "Normal"

        new_order["Quantity"] = quantity
        new_order["Unit_Price"] = round(unit_price, 2)
        new_order["Discount"] = discount_pct

        # Calculate Revenue: Quantity * Unit_Price * (1 - discount_pct/100)
        revenue = quantity * unit_price * (1.0 - (discount_pct / 100.0))
        if is_anomaly and anomaly_type == "negative" and revenue >= 0:
            revenue = -abs(revenue) if revenue != 0 else -5000.0

        new_order["Revenue"] = round(revenue, 2)

        # Recalculate cost and profit
        cost_ratio = random.uniform(0.60, 0.80)
        cost = round(abs(revenue) * cost_ratio, 2)
        new_order["Cost"] = cost
        new_order["Profit"] = round(revenue - cost, 2)

        # New customer occasionally
        if random.random() < 0.20:
            cursor.execute("SELECT COUNT(DISTINCT Customer_ID) FROM sales")
            customer_count = cursor.fetchone()[0] or 5000
            new_order["Customer_ID"] = f"CUST{int(customer_count) + 1:04d}"

        # Insert into database
        columns = list(new_order.index)
        placeholders = ",".join(["?"] * len(columns))
        col_names = ",".join(columns)

        query = f"INSERT INTO sales ({col_names}) VALUES ({placeholders})"
        conn.execute(query, [new_order[col] for col in columns])
        conn.commit()

        return new_order.to_dict()

    finally:
        if should_close_conn:
            conn.close()


def run_live_stream_loop(interval: float = 3.0):
    """Continuous stream loop for standalone CLI execution."""
    ensure_database(verbose=True)
    print("=" * 60)
    print("AI KPI MONITOR - LIVE DATA GENERATOR (OPTIMIZED)")
    print("=" * 60)
    print("Database:", DB_PATH)
    print("Status: LIVE STREAMING")
    print(f"Interval: {interval}s")
    print("=" * 60)

    template_df = get_template_df()

    while True:
        try:
            order = generate_single_order(template_df=template_df)
            anomaly_tag = " [ANOMALY]" if order.get("Anomaly") == "Anomaly" else ""
            print(
                f"[LIVE] Order #{order['Order_ID']} | "
                f"Revenue: Rs. {order['Revenue']:,.2f} | "
                f"Product: {order.get('Product', 'N/A')} | "
                f"Time: {order['Order_Date']}{anomaly_tag}",
                flush=True
            )
        except Exception as e:
            print(f"[ERROR] Live generator error: {e}", file=sys.stderr, flush=True)

        time.sleep(interval)


if __name__ == "__main__":
    interval_val = 3.0
    if len(sys.argv) > 1:
        try:
            interval_val = float(sys.argv[1])
        except ValueError:
            pass
    run_live_stream_loop(interval=interval_val)