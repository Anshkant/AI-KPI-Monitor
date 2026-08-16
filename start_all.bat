@echo off
title AI KPI Monitor - Launcher
echo ========================================================
echo Starting AI KPI Monitor (FastAPI + Generator + Streamlit)
echo ========================================================

start "FastAPI Backend" cmd /k "cd /d %~dp0 && .\venv\Scripts\activate && uvicorn api.main:app --reload --port 8000"
timeout /t 2 >nul

start "Live Order Generator" cmd /k "cd /d %~dp0 && .\venv\Scripts\activate && python src\live_data_generator.py"
timeout /t 1 >nul

start "Streamlit Dashboard" cmd /k "cd /d %~dp0 && .\venv\Scripts\activate && streamlit run dashboard\dashboard\app.py"

echo All services launched!
