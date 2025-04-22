@echo off
setlocal

REM Chạy FastAPI server (chạy ngầm bằng start)
start "" uvicorn api_server:app --host 0.0.0.0 --port 8881 --reload

REM Chờ 3 giây để chắc chắn API đã start
timeout /t 3 /nobreak >nul

REM Chạy public_port.py
REM python D:\source-dev\setup\reverse_tunnel_client\src\public_port\public_port.py

endlocal
