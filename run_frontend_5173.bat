@echo off
title buisyvizzy Frontend Server (:5173)
echo =======================================================
echo Starting buisyvizzy Frontend on http://localhost:5173
echo Authoritative Backend link: http://localhost:8000
echo =======================================================
"C:\Users\Varad\anaconda3\python.exe" backend\serve_frontend_5173.py
pause
