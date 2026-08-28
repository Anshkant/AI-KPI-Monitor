@echo off
title AI KPI Monitor - Launcher
echo ========================================================
echo Starting AI KPI Monitor (FastAPI + Generator + Streamlit)
echo ========================================================

echo [1/4] Checking and initializing database...
call .\venv\Scripts\activate
python database\init_db.py

echo.
echo [2/4] Launching FastAPI Backend...
start "FastAPI Backend" cmd /k "cd /d %~dp0 && .\venv\Scripts\activate && uvicorn api.main:app --reload --port 8000"
timeout /t 2 >nul

echo [3/4] Launching Live Order Generator...
start "Live Order Generator" cmd /k "cd /d %~dp0 && .\venv\Scripts\activate && python src\live_data_generator.py"
timeout /t 1 >nul

echo [4/4] Launching Streamlit Dashboard...
start "Streamlit Dashboard" cmd /k "cd /d %~dp0 && .\venv\Scripts\activate && streamlit run dashboard\dashboard\app.py"

echo.
echo ========================================================
echo All services launched successfully!
echo ========================================================

