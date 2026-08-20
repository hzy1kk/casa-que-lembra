@echo off
cd /d "%~dp0"
echo.
echo  A Casa que Lembra — servidor local
echo  Abrindo http://localhost:8000
echo  CTRL+C para encerrar
echo.
start "" "http://localhost:8000"
python -m http.server 8000
pause
