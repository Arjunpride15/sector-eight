@echo off
REM Safely stop Sector Eight
taskkill /IM python.exe >nul 2>&1

call se_env\Scripts\activate
python auth.pyw