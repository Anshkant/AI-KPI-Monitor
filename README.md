# 🚀 AI KPI Monitor

### Real-Time Executive Sales Intelligence & Operational Risk Monitoring

AI KPI Monitor is a real-time sales intelligence platform designed to monitor **sales performance, live transactions, business KPIs and operational anomalies** through an interactive executive dashboard.

The system combines **Python, Pandas, SQLite, FastAPI and Streamlit** to create a complete data pipeline that continuously generates realistic live sales transactions, stores them in a database, exposes them through REST APIs and visualizes changing business metrics in real time.

---

## 🌐 Live Demo

### 📊 Streamlit Executive Dashboard

https://ai-kpi-monitor-fretrq5tubcf47uqgfujvn.streamlit.app/

### ⚡ FastAPI Backend

https://ai-kpi-monitor.onrender.com/

### 🔌 API Endpoints

- `GET /sales/dashboard-summary`
- `GET /sales/latest`

---

# 🎯 Project Overview

Traditional dashboards mainly focus on historical reporting.

AI KPI Monitor goes a step further by introducing a **live sales monitoring pipeline** that continuously processes new transactions and updates business metrics.

The application provides:

- Real-time sales KPIs
- Live transaction monitoring
- Operational anomaly detection
- Revenue and profitability analysis
- Region and category analysis
- Sales channel analysis
- AI-assisted business intelligence
- REST API integration
- Automated live transaction generation

---

# 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │    Sales Dataset     │
                    │      CSV / CSV.GZ    │
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
        │ Generator        │      │    REST API      │
        └────────┬─────────┘      └────────┬─────────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                    ┌──────────────────────┐
                    │ Streamlit Executive  │
                    │      Dashboard       │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       KPI Monitoring    Anomaly Radar    AI Insights




---

# ✨ Key Features

### 📊 Real-Time Executive KPI Dashboard
- Live Gross Revenue monitoring
- Total Orders tracking
- Active Customers monitoring
- Average Order Value (AOV)
- Net Profit and Profit Margin
- Dynamic KPI updates from backend data

### ⚡ Live Sales Stream
- Automatically generates realistic sales transactions
- Configurable polling interval
- Real-time order injection for demonstration
- Latest transaction visibility
- Continuous backend synchronization

### 🚨 AI-Powered Anomaly Detection
- Real-time anomaly monitoring
- Detects unusual sales transactions
- Supports multiple anomaly patterns:
  - Extremely unusual revenue
  - Extremely unusual order quantity
  - Heavy discount transactions
  - Negative revenue transactions
- Severity-based alert system:
  - 🔴 Critical
  - 🟠 High
  - 🟡 Medium

### 🤖 AI Business Intelligence
- Automated business performance insights
- Revenue and profit analysis
- Trend identification
- Operational risk interpretation
- Executive-level business recommendations

### 🌐 REST API Backend
- FastAPI-powered backend architecture
- Dashboard summary API
- Latest transactions API
- Backend health monitoring
- Clean separation between frontend and backend

### 🗄️ SQLite Data Layer
- Persistent sales transaction storage
- SQLite-based analytical database
- Optimized database access
- Supports continuous live transaction insertion
- WAL mode for improved concurrent read/write performance

### 🎛️ Interactive Executive Controls
- Reporting period selection
- Region filtering
- Category filtering
- Sales channel filtering
- Live stream toggle
- Adjustable polling rate
- Manual test transaction injection

### 📈 Business Analytics
- Monthly revenue trends
- Profit trends
- Regional performance
- Category performance
- Sales channel analysis
- Top-performing products

### 🔄 Production-Style Architecture
- Streamlit frontend
- FastAPI backend
- SQLite database
- Python data processing layer
- Modular source-code structure
- REST-based frontend/backend communication

---

# 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive executive dashboard |
| FastAPI | REST API backend |
| SQLite | Transaction database |
| Pandas | Data processing & analysis |
| NumPy | Numerical computations |
| Plotly | Interactive visualizations |
| Uvicorn | FastAPI server |
| Git & GitHub | Version control |
| Render | Backend deployment |
| Streamlit Cloud | Dashboard deployment |

---

# 📁 Project Structure

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
│   ├── raw/
│   ├── processed/
│   └── database/
│       ├── init_db.py
│       └── sales.db
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
├── .env
├── README.md
└── requirements.txt
