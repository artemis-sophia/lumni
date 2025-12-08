@echo off
REM Lumni - Initialization Script (Windows)
REM This script helps set up the gateway for first-time use

echo.
echo ============================================
echo   Lumni API Gateway - Initialization
echo ============================================
echo.

REM Check if config.json exists
if not exist "config.json" (
    echo Creating config.json from example...
    copy config.example.json config.json
    echo Created config.json
    echo.
    echo Please edit config.json and add your API keys!
    echo.
) else (
    echo config.json already exists
)

REM Check if .env exists
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env from example...
        copy .env.example .env
        echo Created .env
        echo.
        echo Please edit .env and add your API keys!
        echo.
    ) else (
        echo .env.example not found, creating basic .env file...
        (
            echo # Unified API Key
            echo UNIFIED_API_KEY=your-unified-api-key-here
            echo.
            echo # Provider API Keys
            echo GROQ_API_KEY=your_groq_key_here
            echo DEEPSEEK_API_KEY=your_deepseek_key_here
            echo.
            echo # Logging
            echo LOG_LEVEL=info
            echo CONFIG_PATH=./config.json
        ) > .env
        echo Created basic .env file
        echo Please edit .env and add your API keys!
        echo.
    )
) else (
    echo .env already exists
)

REM Create necessary directories
echo Creating directories...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
echo Directories created

REM Check Python version
echo.
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.11+ required. Please install Python.
    exit /b 1
)
python --version
echo Python found

REM Check if Poetry is installed
poetry --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo Poetry not found. Installing dependencies with pip...
    if exist "requirements.txt" (
        pip install -r requirements.txt
    ) else (
        echo ERROR: requirements.txt not found
        exit /b 1
    )
) else (
    echo.
    echo Installing dependencies with Poetry...
    poetry install
    echo Dependencies installed
)

REM Initialize database
echo.
echo Initializing database...
if exist "poetry.bat" (
    poetry run alembic upgrade head
) else (
    python -m alembic upgrade head
)
echo Database initialized

echo.
echo ============================================
echo   Setup complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit config.json and add your API keys
echo 2. Edit .env and set your unified API key
echo 3. Run 'poetry run uvicorn app.main:app --host 0.0.0.0 --port 3000' to start the gateway
echo    Or use: 'python -m uvicorn app.main:app --host 0.0.0.0 --port 3000'
echo.
echo For detailed setup instructions, see SETUP.md
echo.

