@echo off
set PYTHON_EXE=C:\Users\Varad\AppData\Local\Programs\Python\Python314\python.exe
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
)
cd /d "%~dp0"
"%PYTHON_EXE%" backend\demo_optimization_comparison.py
pause
