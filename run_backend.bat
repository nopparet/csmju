@echo off
title Smart Kiosk — Backend
cd /d "c:\Users\Lenovo\OneDrive\เอกสาร\smart-kiosk\backend"
echo Starting backend...
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
