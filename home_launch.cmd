@echo off
REM Safely stop Sector Eight
taskkill /IM python.exe >nul 2>&1
timeout /t 1 /nobreak >nul
call se_env\Scripts\activate
python home.pyw