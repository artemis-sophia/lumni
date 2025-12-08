@echo off
REM Lumni - One-Command Setup Script (Windows)
REM This script sets up the entire project in one go

echo.
echo ============================================
echo   Lumni API Gateway - Quick Setup
echo ============================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.11+ required. Please install Python.
    exit /b 1
)
python --version
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip and install build tools
echo Upgrading pip and installing build tools...
python -m pip install --upgrade pip setuptools wheel
echo.

REM Install package in editable mode
echo Installing Lumni package and dependencies...
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install package
    exit /b 1
)
echo Package installed in editable mode
echo.

REM Copy configuration files
echo Setting up configuration...
if not exist "config.json" (
    copy config.example.json config.json
    echo Created config.json from example
) else (
    echo config.json already exists
)

if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo Created .env from example
    ) else (
        echo .env.example not found, skipping .env creation
    )
) else (
    echo .env already exists
)
echo.

REM Create directories
echo Creating directories...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
echo Directories created
echo.

REM Initialize database
echo Initializing database...
alembic upgrade head
if errorlevel 1 (
    echo ERROR: Failed to initialize database
    exit /b 1
)
echo Database initialized
echo.

echo ============================================
echo   Setup complete!
echo ============================================
echo.
echo IMPORTANT: Before starting the gateway:
echo   1. Edit config.json and add your API keys
echo   2. Edit .env and set your unified API key
echo.
echo To start the gateway:
echo   venv\Scripts\activate
echo   uvicorn app.main:app --host 0.0.0.0 --port 3000
echo.
echo To use the CLI:
echo   venv\Scripts\activate
echo   lumni --help
echo.
echo For detailed instructions, see QUICKSTART.md or SETUP.md
echo.
