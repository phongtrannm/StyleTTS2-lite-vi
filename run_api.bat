@echo off
cd /d %~dp0\api
echo Running FastAPI server from: %CD%\api_server.py
uvicorn api_server:app --host 0.0.0.0 --port 8881 --reload
pause
