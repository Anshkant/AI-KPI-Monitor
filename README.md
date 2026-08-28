# AI KPI Monitor 📊⚡

> Executive Sales Intelligence & Real-Time Operational Risk Radar

An enterprise-grade, real-time KPI monitoring and anomaly detection dashboard powered by **FastAPI**, **SQLite WAL**, and **Streamlit**.

---

## 🚀 Quick Start

### 1. Launch Everything (One-Click / Unified)
On Windows:
```cmd
start_all.bat
```

Or cross-platform (Windows / Linux / macOS / Docker / Cloud):
```bash
python run.py
```

> **Note on Database**: `database/sales.db` is auto-initialized on first run from compressed seed data (`data/processed/anomaly_sales_data.csv.gz`). There is no need to manually create the database upon cloning or deployment.

### 2. Manual Startup
```powershell
# Terminal 1 - FastAPI Backend (Auto-initializes DB if missing)
.\venv\Scripts\activate
uvicorn api.main:app --reload --port 8000

# Terminal 2 - Real-Time Live Order Streamer
.\venv\Scripts\activate
python src\live_data_generator.py

# Terminal 3 - Streamlit Executive Dashboard
.\venv\Scripts\activate
streamlit run dashboard\dashboard\app.py
```

Open your browser at **`http://localhost:8501`**.

---

## 📁 Project Architecture

```
AI-KPI-Monitor/
├── api/
│   └── main.py                 # FastAPI backend with high-speed SQL aggregations
├── dashboard/
│   └── dashboard/
│       └── app.py              # Streamlit live executive dashboard
├── data/                       # Compressed high-performance datasets (.csv.gz)
│   ├── processed/
│   │   ├── anomaly_sales_data.csv.gz
│   │   └── clean_sales_data.csv.gz
│   └── raw/
│       └── retail_sales_dataset.csv.gz
├── database/
│   ├── init_db.py              # Database initializer with WAL & indexing
│   └── sales.db                # SQLite database (Indexed & WAL enabled)
├── reports/
│   └── AI_Business_Summary.txt # AI generated summary report
├── src/
│   ├── ai_summary.py           # Gemini AI executive business insight generator
│   ├── anomaly_detector.py     # IsolationForest anomaly detection model
│   ├── clean_data.py           # Data cleaning pipeline
│   ├── data_loader.py          # Unified compressed data loader
│   ├── dataset_generator.py    # Synthetic dataset generator
│   ├── eda.py                  # Exploratory Data Analysis
│   ├── kpi_calculator.py       # Terminal business KPI calculator
│   └── live_data_generator.py  # Concurrent live order streaming generator
├── start_all.bat               # One-click multi-service launcher
└── .env                        # API keys and environment variables
```

---

## ⚡ Key Features
- **Instant Pre-Aggregated Summary (< 10ms)**: Sub-10ms response time via SQLite SQL groupings.
- **Concurrent Live Ingestion**: Lock-free concurrent read/writes using SQLite WAL mode.
- **Dynamic Stream Sync**: Real-time order synchronization with live status badge and customizable polling rate (2s–10s).
- **IsolationForest Anomaly Radar**: Real-time detection of high/critical operational risks with automated severity classifications.
- **Enterprise SVG Icon System**: Clean, responsive UI with interactive Plotly visual analytics.
