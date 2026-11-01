@echo off
set PYTHON_EXE=C:\Users\Varad\anaconda3\python.exe
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
)
cd /d "%~dp0\backend"
echo ===================================================================
echo   Starting Supply Chain Digital Twin API Server...
echo   Opening Swagger UI at: http://localhost:8000/docs
echo ===================================================================
start "" "http://localhost:8000/docs"
"%PYTHON_EXE%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
