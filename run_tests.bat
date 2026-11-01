@echo off
set PYTHON_EXE=C:\Users\Varad\anaconda3\python.exe
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=C:\Users\Varad\AppData\Local\Programs\Python\Python314\python.exe
)
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
)
cd /d "%~dp0"
"%PYTHON_EXE%" -m pytest backend\tests -v
pause
