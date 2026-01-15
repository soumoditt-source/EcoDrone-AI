@echo off
echo ============================================
echo      EcoDrone AI - Startup Script
echo      Built by Soumoditya Das
echo ============================================

echo [1/3] Installing Backend Dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Warning: Pip install had issues. Attempting to continue...
)

echo [2/3] Starting Backend Server (Port 8000)...
start "EcoDrone Backend" cmd /k "python -m uvicorn app.main:app --reload --port 8000"

echo [3/3] Starting Frontend (Port 5173)...
cd ../frontend
call npm install
start "EcoDrone Frontend" cmd /k "npm run dev"

echo ============================================
echo System Running!
echo Frontend: http://localhost:5173
echo Backend: http://localhost:8000/docs
echo ============================================
pause
