@echo off
REM ==============================================================================
REM ProcureShield AI — Windows Startup Script
REM ==============================================================================
echo Starting ProcureShield AI...

cd /d "%~dp0"

REM 1. Backend Setup
if not exist "backend\venv" (
    echo Creating virtual environment...
    python -m venv backend\venv
)

call backend\venv\Scripts\activate
pip install -q -r backend\requirements.txt

REM 2. Start Backend
start "ProcureShield Backend" cmd /k "call backend\venv\Scripts\activate && set PYTHONPATH=. && uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

REM 3. Start Frontend
if exist "frontend\package.json" (
    cd frontend
    if not exist "node_modules" (
        echo Installing node modules...
        npm install
    )
    start "ProcureShield Frontend" cmd /k "npm run dev -- --host 127.0.0.1 --port 5173"
    cd ..
)

echo.
echo ==========================================================
echo   ProcureShield AI started in separate windows!
echo   Frontend: http://127.0.0.1:5173
echo   Backend:  http://127.0.0.1:8000
echo   Docs:     http://127.0.0.1:8000/docs
echo ==========================================================
pause
