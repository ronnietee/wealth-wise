@echo off
REM Batch script for Windows Task Scheduler
REM This script loads environment variables from .env and runs the renewal processor

cd /d "%~dp0\.."

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found
    exit /b 1
)

REM Load .env file (basic parsing)
for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
    set "line=%%a"
    if not "!line:~0,1!"=="#" (
        set "%%a"
    )
)

REM Set default APP_URL if not set
if "%APP_URL%"=="" set APP_URL=http://localhost:5000

REM Ensure required variables are set
if "%ADMIN_USERNAME%"=="" (
    echo ERROR: ADMIN_USERNAME must be set in .env file
    exit /b 1
)
if "%ADMIN_PASSWORD%"=="" (
    echo ERROR: ADMIN_PASSWORD must be set in .env file
    exit /b 1
)

REM Run Python script
python scripts\process_renewals.py >> logs\renewals.log 2>&1

exit /b %ERRORLEVEL%

