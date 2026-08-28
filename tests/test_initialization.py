import os
import sys
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.init_db import DB_PATH, is_database_initialized, ensure_database, init_database
from fastapi.testclient import TestClient
from api.main import app

def test_missing_db_and_api_lifespan():
    print("\n[TEST 1] Testing missing database scenario...")
    backup_path = DB_PATH + ".bak"
    if os.path.exists(DB_PATH):
        shutil.move(DB_PATH, backup_path)

    # Clean any temporary wal/shm files
    for ext in ["-wal", "-shm", "-journal"]:
        if os.path.exists(DB_PATH + ext):
            os.remove(DB_PATH + ext)

    try:
        # Verify DB is currently missing
        assert not is_database_initialized(DB_PATH), "DB should report uninitialized when missing"
        print("[PASS] Confirmed DB does not exist.")

        # Test FastAPI Lifespan startup
        print("\n[TEST 2] Starting FastAPI with TestClient (triggering Lifespan)...")
        with TestClient(app) as client:
            # Check DB got initialized
            assert is_database_initialized(DB_PATH), "DB should be initialized after lifespan startup"
            print("[PASS] Confirmed DB auto-initialized during API startup.")

            # Test API endpoints
            resp_root = client.get("/")
            assert resp_root.status_code == 200, f"Root failed: {resp_root.text}"
            print("[PASS] GET / -> 200 OK")

            resp_kpis = client.get("/kpis")
            assert resp_kpis.status_code == 200, f"KPIs failed: {resp_kpis.text}"
            data_kpis = resp_kpis.json()
            assert data_kpis["revenue"] > 0, "Revenue should be > 0"
            assert data_kpis["orders"] > 0, "Orders should be > 0"
            print(f"[PASS] GET /kpis -> Revenue: {data_kpis['revenue']:,.2f}, Orders: {data_kpis['orders']:,}")

            resp_summary = client.get("/sales/dashboard-summary")
            assert resp_summary.status_code == 200, f"Summary failed: {resp_summary.text}"
            data_sum = resp_summary.json()
            assert data_sum["total_monitored"] > 0
            print(f"[PASS] GET /sales/dashboard-summary -> Monitored: {data_sum['total_monitored']:,}")

            resp_filter = client.get("/sales/filter-options")
            assert resp_filter.status_code == 200
            data_filt = resp_filter.json()
            assert len(data_filt["regions"]) > 0
            print(f"[PASS] GET /sales/filter-options -> Regions: {len(data_filt['regions'])}, Categories: {len(data_filt['categories'])}")

            resp_anomalies = client.get("/anomalies/latest?limit=5")
            assert resp_anomalies.status_code == 200
            print(f"[PASS] GET /anomalies/latest -> Found {len(resp_anomalies.json()['data'])} anomalies")

        print("\n[TEST 3] Testing Idempotency (subsequent runs should skip)...")
        skipped = not init_database(force=False, verbose=True)
        assert skipped, "Subsequent init should be skipped"
        print("[PASS] Idempotency verified: re-running init does not reload needlessly.")

        print("\n=======================================================")
        print("?? ALL DATABASE & API LIFESPAN TESTS PASSED PERFECTLY!")
        print("=======================================================")

    finally:
        if os.path.exists(backup_path):
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
            shutil.move(backup_path, DB_PATH)

if __name__ == "__main__":
    test_missing_db_and_api_lifespan()
