import sqlite3
import pandas as pd
import os

# Project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# CSV path
CSV_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "anomaly_sales_data.csv"
)
if not os.path.exists(CSV_PATH):
    CSV_PATH = os.path.join(
        BASE_DIR,
        "data",
        "processed",
        "anomaly_sales_data.csv.gz"
    )

# Database path
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "sales.db")

# Create database folder
os.makedirs(DB_DIR, exist_ok=True)

# Load anomaly dataset (auto-handles gzip)
df = pd.read_csv(CSV_PATH)


# Create SQLite database
conn = sqlite3.connect(DB_PATH)

# Save data into sales table
df.to_sql(
    "sales",
    conn,
    if_exists="replace",
    index=False
)

# Enable WAL mode and create indexes for ultra-fast queries
conn.execute("PRAGMA journal_mode=WAL;")
conn.execute("CREATE INDEX IF NOT EXISTS idx_order_id ON sales(Order_ID DESC);")
conn.execute("CREATE INDEX IF NOT EXISTS idx_order_date ON sales(Order_Date);")
conn.execute("CREATE INDEX IF NOT EXISTS idx_anomaly ON sales(Anomaly);")
conn.commit()
conn.close()

print("=" * 60)
print("DATABASE INITIALIZATION COMPLETED (WAL & INDEXED)")
print("=" * 60)
print("Records :", len(df))
print("Database:", DB_PATH)
print("Table   : sales")
print("=" * 60)