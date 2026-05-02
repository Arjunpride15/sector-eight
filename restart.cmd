@echo off
REM Safely stop Sector Eight
taskkill /FI "WINDOWTITLE eq Sector 8*" /F >nul 2>&1
timeout /t 2 /nobreak >nul
call se_env\Scripts\activate
python main.pyw
