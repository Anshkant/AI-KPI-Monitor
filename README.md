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
