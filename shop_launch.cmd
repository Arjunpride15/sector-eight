@echo off
REM Safely stop Sector Eight
taskkill /FI "WINDOWTITLE eq Sector 8*" /F >nul 2>&1
timeout /t 1 /nobreak >nul
call se_env\Scripts\activate
python shop.pyw