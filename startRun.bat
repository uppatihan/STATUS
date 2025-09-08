@echo off
set PYTHON=D:\YUP\UPY CODING\STATUS\backend\.venv\Scripts\python.exe
set APP=D:\YUP\UPY CODING\STATUS\backend\main.py
set LOG=D:\YUP\UPY CODING\STATUS\backend\log.log
set PUBLIC=D:\YUP\UPY CODING\STATUS\public

echo Starting Flask server, logging to %LOG%...
start "" "%PYTHON%" "%APP%" >> "%LOG%" 2>&1

echo Starting HTTP server on port 8000 serving %PUBLIC%...
cd /d %PUBLIC%
start "" "%PYTHON%" -m http.server 8000

pause
