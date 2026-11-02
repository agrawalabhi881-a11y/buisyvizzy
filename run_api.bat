@echo off
set PYTHON_EXE=C:\Users\Varad\anaconda3\python.exe
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
)
cd /d "%~dp0\backend"
echo ===================================================================
echo   Starting NEXUS Supply Chain Digital Twin Platform...
echo   Opening Web App at:   http://localhost:8000/web
echo   Opening Swagger UI at: http://localhost:8000/docs
echo ===================================================================
start "" "http://localhost:8000/web"
start "" "http://localhost:8000/docs"
"%PYTHON_EXE%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
