# 🚀 AI KPI Monitor

### Real-Time Executive Sales Intelligence & Operational Risk Monitoring

AI KPI Monitor is a real-time sales intelligence platform that combines **FastAPI, Streamlit, SQLite, Python, Pandas and AI-driven business insights** to monitor sales KPIs, live transactions and operational anomalies through an executive dashboard.

The system continuously generates realistic live sales transactions, stores them in a SQLite database, exposes them through REST APIs and visualizes changing business KPIs in an interactive executive dashboard.

---

## 🌐 Live Demo

### 📊 Streamlit Dashboard
https://ai-kpi-monitor-fretrq5tubcf47uqgfujvn.streamlit.app/

### ⚡ FastAPI Backend
https://ai-kpi-monitor.onrender.com/

### 🔌 API Endpoints

- `/sales/dashboard-summary`
- `/sales/latest`

---

# 🎯 Project Overview

Traditional dashboards usually provide historical reports but do not continuously monitor operational changes.

AI KPI Monitor addresses this by creating a **live sales monitoring pipeline**:

```text
                    ┌──────────────────────┐
                    │   Sales Dataset      │
                    │      CSV / CSV.GZ     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   SQLite Database    │
                    │      sales.db        │
                    └──────────┬───────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  ▼                         ▼
        ┌──────────────────┐      ┌──────────────────┐
        │ Live Order       │      │ FastAPI Backend  │
        │ Generator        │      │ REST API         │
        └────────┬─────────┘      └────────┬─────────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                    ┌──────────────────────┐
                    │ Streamlit Executive  │
                    │ Dashboard            │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
         KPI Monitoring   Anomaly Radar   AI Insights









## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Pandas | Data processing & analysis |
| SQLite | Transactional data storage |
| FastAPI | REST API backend |
| Streamlit | Interactive executive dashboard |
| SQL | KPI aggregation & querying |
| Git & GitHub | Version control |
| Render | Backend deployment |
| Streamlit Cloud | Dashboard deployment |


## 📊 Dashboard Features

### Executive KPI Monitoring
- Gross Revenue
- Total Orders
- Active Customers
- Average Order Value
- Net Profit
- Profit Margin

### Operational Risk Radar
- Critical Alerts
- High Severity Alerts
- Medium Severity Alerts
- Total Active Anomalies
- Anomaly reason classification

### Live Monitoring
- Latest transaction
- Live order count
- Real-time transaction stream
- Configurable polling interval
- Test live-order injection


## 📁 Project Structure

```text
AI-KPI-Monitor/
│
├── api/
│   └── main.py
│
├── dashboard/
│   └── dashboard/
│       └── app.py
│
├── data/
│   ├── processed/
│   └── raw/
│
├── database/
│   ├── init_db.py
│   └── sales.db
│
├── reports/
│   └── AI_Business_Summary.txt
│
├── src/
│   ├── ai_summary.py
│   ├── anomaly_detector.py
│   ├── clean_data.py
│   ├── data_loader.py
│   ├── dataset_generator.py
│   ├── eda.py
│   ├── kpi_calculator.py
│   └── live_data_generator.py
│
├── tests/
│
├── .gitignore
├── requirements.txt
└── README.md


```markdown
### 📂 Core Modules

- `src/live_data_generator.py` — Generates realistic live sales transactions.
- `src/anomaly_detector.py` — Detects unusual sales patterns and classifies anomalies.
- `src/kpi_calculator.py` — Calculates business KPIs such as revenue, profit and margins.
- `src/ai_summary.py` — Generates AI-assisted business intelligence summaries.
- `src/data_loader.py` — Handles sales data loading and preparation.
- `src/clean_data.py` — Cleans and preprocesses the dataset.
- `src/dataset_generator.py` — Generates/creates sales datasets for the application.
- `src/eda.py` — Performs exploratory data analysis.
- `database/init_db.py` — Initializes and indexes the SQLite sales database.
- `api/main.py` — FastAPI backend and REST API endpoints.
- `dashboard/dashboard/app.py` — Streamlit executive dashboard.
