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
