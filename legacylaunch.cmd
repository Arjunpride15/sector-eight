@echo off
REM Check if the -reset flag was passed as the first argument
if "%1"=="-reset" (
    del game_data* /q 2>nul
    echo [DEV] Data reset: Binary shelf files deleted.
)

REM Activate the virtual environment and run Sector 8
call se_env\Scripts\activate
python main.pyw