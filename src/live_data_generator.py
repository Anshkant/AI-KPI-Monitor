import sqlite3
import pandas as pd
import random
import time
import os
import sys
from datetime import datetime

# Project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database
DB_PATH = os.path.join(BASE_DIR, "database", "sales.db")

# Original dataset
CSV_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "anomaly_sales_data.csv"
)

# Load existing sales data as templates
if not os.path.exists(CSV_PATH):
    # Fallback to clean_sales_data if anomaly_sales_data not found
    CSV_PATH = os.path.join(BASE_DIR, "data", "processed", "clean_sales_data.csv")

df = pd.read_csv(CSV_PATH)

# Convert date
if "Order_Date" in df.columns:
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn

# Ensure WAL mode is active on database
try:
    init_conn = get_connection()
    init_conn.close()
except Exception as e:
    print(f"Initial DB check warning: {e}")

print("=" * 60)
print("AI KPI MONITOR - LIVE DATA GENERATOR (OPTIMIZED)")
print("=" * 60)
print("Database:", DB_PATH)
print("Status: LIVE STREAMING")
print("=" * 60)

interval = 3  # Generate new order every 3-5 seconds

while True:
    try:
        # Select random existing order as template
        new_order = df.sample(1).iloc[0].copy()

        conn = get_connection()

        # Generate new Order ID
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(MAX(Order_ID), 100000) FROM sales")
            max_order_id = cursor.fetchone()[0]
            new_order["Order_ID"] = int(max_order_id) + 1
        except Exception as err:
            new_order["Order_ID"] = int(time.time())

        # Current date/time
        new_order["Order_Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Generate realistic quantity
        new_order["Quantity"] = random.randint(1, 10)

        # Realistic revenue & discounts
        unit_price = float(new_order.get("Unit_Price", random.randint(500, 25000)))
        discount = float(new_order.get("Discount", random.choice([0.0, 0.05, 0.1, 0.15, 0.2])))

        # 5% chance of unusual price/quantity anomaly for live detection
        is_anomaly = random.random() < 0.08
        if is_anomaly:
            anomaly_type = random.choice(["huge_qty", "heavy_discount", "high_rev", "negative"])
            if anomaly_type == "huge_qty":
                new_order["Quantity"] = random.randint(25, 60)
            elif anomaly_type == "heavy_discount":
                discount = 0.65
            elif anomaly_type == "high_rev":
                unit_price = unit_price * random.uniform(4.0, 8.0)
            new_order["Anomaly"] = "Anomaly"
        else:
            new_order["Anomaly"] = "Normal"

        new_order["Unit_Price"] = unit_price
        new_order["Discount"] = discount
        new_order["Revenue"] = round(new_order["Quantity"] * unit_price * (1 - discount), 2)

        # Recalculate cost and profit
        cost_ratio = random.uniform(0.60, 0.80)
        new_order["Cost"] = round(new_order["Revenue"] * cost_ratio, 2)
        new_order["Profit"] = round(new_order["Revenue"] - new_order["Cost"], 2)

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
        conn.close()

        anomaly_tag = " 🚨 [ANOMALY]" if new_order.get("Anomaly") == "Anomaly" else ""
        print(
            f"[LIVE] Order #{new_order['Order_ID']} | "
            f"Revenue: ₹{new_order['Revenue']:,.2f} | "
            f"Product: {new_order.get('Product', 'N/A')} | "
            f"Time: {new_order['Order_Date']}{anomaly_tag}",
            flush=True
        )

    except Exception as e:
        print(f"[ERROR] Live generator error: {e}", file=sys.stderr, flush=True)

    time.sleep(interval)