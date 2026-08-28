import os
import sys
import time
import subprocess
import signal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.init_db import ensure_database

def main():
    print("=" * 65)
    print("AI KPI MONITOR - UNIFIED LAUNCHER")
    print("=" * 65)

    # 1. Ensure database
    print("\n[Step 1/3] Verifying / Initializing SQLite Database...")
    ensure_database(verbose=True)

    if "--init-only" in sys.argv:
        print("\nDatabase initialization complete. Exiting (--init-only).")
        return

    processes = []

    def cleanup(signum=None, frame=None):
        print("\n[Shutting down] Terminating child services...")
        for p in processes:
            if p.poll() is None:
                p.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    python_executable = sys.executable

    try:
        # 2. Start FastAPI Backend
        print("\n[Step 2/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...")
        api_process = subprocess.Popen(
            [python_executable, "-m", "uvicorn", "api.main:app", "--port", "8000"],
            cwd=BASE_DIR
        )
        processes.append(api_process)
        time.sleep(2)

        # 3. Start Live Generator (optional with --no-generator)
        if "--no-generator" not in sys.argv:
            print("[Optional] Starting Live Data Stream Generator...")
            gen_process = subprocess.Popen(
                [python_executable, "src/live_data_generator.py"],
                cwd=BASE_DIR
            )
            processes.append(gen_process)
            time.sleep(1)

        # 4. Start Streamlit Dashboard
        print("\n[Step 3/3] Starting Streamlit Executive Dashboard...")
        print("Dashboard will be available at http://localhost:8501")
        print("Press Ctrl+C to stop all services.\n")
        dashboard_process = subprocess.Popen(
            [python_executable, "-m", "streamlit", "run", "dashboard/dashboard/app.py"],
            cwd=BASE_DIR
        )
        processes.append(dashboard_process)

        # Wait for processes
        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        cleanup()
    except Exception as err:
        print(f"\n[Launcher Error] {err}")
        cleanup()

if __name__ == "__main__":
    main()
