@echo off
title Install Requirements for WeCare247 Automation
echo Installing requirements for WeCare247 Churn Prediction Automation...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

echo Installing Python packages...
pip install -r requirements.txt

if %errorlevel% eq 0 (
    echo.
    echo SUCCESS: All requirements installed successfully!
    echo You can now run the automation using run_automation.bat
) else (
    echo.
    echo ERROR: Failed to install some requirements
    echo Please check the error messages above
)

pause
