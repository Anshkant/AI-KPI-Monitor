import os
import sys
import sqlite3
import pandas as pd

# Project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database paths
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "sales.db")


def is_database_initialized(db_path: str = DB_PATH) -> bool:
    """Checks if the SQLite database exists, contains the 'sales' table, and has data."""
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        return False

    try:
        conn = sqlite3.connect(db_path, timeout=5)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sales';"
        )
        table_exists = cursor.fetchone() is not None
        if not table_exists:
            conn.close()
            return False

        cursor.execute("SELECT COUNT(*) FROM sales;")
        row_count = cursor.fetchone()[0]
        conn.close()
        return row_count > 0
    except Exception:
        return False


def find_source_data() -> str:
    """Locates the primary or fallback sales dataset, checking uncompressed and gzip versions."""
    candidate_paths = [
        os.path.join(BASE_DIR, "data", "processed", "anomaly_sales_data.csv"),
        os.path.join(BASE_DIR, "data", "processed", "anomaly_sales_data.csv.gz"),
        os.path.join(BASE_DIR, "data", "processed", "clean_sales_data.csv"),
        os.path.join(BASE_DIR, "data", "processed", "clean_sales_data.csv.gz"),
        os.path.join(BASE_DIR, "data", "raw", "retail_sales_dataset.csv"),
        os.path.join(BASE_DIR, "data", "raw", "retail_sales_dataset.csv.gz"),
        os.path.join(BASE_DIR, "data", "retail_sales_dataset.csv"),
    ]

    for path in candidate_paths:
        if os.path.exists(path):
            return path

    raise FileNotFoundError(
        "Could not find any seed dataset in data/processed/ or data/raw/. "
        "Please ensure at least one dataset file (.csv or .csv.gz) exists."
    )


def init_database(force: bool = False, verbose: bool = True) -> bool:
    """
    Initializes the SQLite database if it does not already exist or if force=True.
    Returns True if initialized, False if already initialized and skipped.
    """
    if not force and is_database_initialized(DB_PATH):
        if verbose:
            print(f"[DB] Database already initialized at: {DB_PATH} (skipping creation)")
        return False

    if verbose:
        print("=" * 60)
        print("INITIALIZING DATABASE...")
        print("=" * 60)

    # Ensure target directory exists
    os.makedirs(DB_DIR, exist_ok=True)

    # Locate and load data
    source_path = find_source_data()
    if verbose:
        print(f"[DB] Loading seed data from: {os.path.relpath(source_path, BASE_DIR)}")

    # pandas read_csv automatically handles .gz compressed CSVs
    df = pd.read_csv(source_path)

    # Ensure required columns are present
    if "Anomaly" not in df.columns:
        df["Anomaly"] = "Normal"

    # Create SQLite database with WAL mode configured first
    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA busy_timeout=10000;")
    conn.execute("PRAGMA journal_mode=WAL;")

    try:
        # Save data into sales table
        df.to_sql("sales", conn, if_exists="replace", index=False)

        # Create indexes for ultra-fast queries
        conn.execute("CREATE INDEX IF NOT EXISTS idx_order_id ON sales(Order_ID DESC);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_order_date ON sales(Order_Date);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_anomaly ON sales(Anomaly);")
        if "Region" in df.columns:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_region ON sales(Region);")
        if "Category" in df.columns:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON sales(Category);")
        if "Sales_Channel" in df.columns:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sales_channel ON sales(Sales_Channel);")

        conn.commit()

        if verbose:
            print("=" * 60)
            print("DATABASE INITIALIZATION COMPLETED (WAL & INDEXED)")
            print("=" * 60)
            print(f"Records  : {len(df):,}")
            print(f"Database : {DB_PATH}")
            print(f"Table    : sales")
            print("=" * 60)

        return True

    finally:
        conn.close()


def ensure_database(verbose: bool = True) -> bool:
    """Convenience helper to ensure the database exists and is populated before running any operations."""
    return init_database(force=False, verbose=verbose)


if __name__ == "__main__":
    force_flag = "--force" in sys.argv or "-f" in sys.argv
    init_database(force=force_flag, verbose=True)