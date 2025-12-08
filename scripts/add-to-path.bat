@echo off
REM Script to add Lumni CLI to PATH (Windows)
REM This script helps you add the lumni command to your PATH

echo Lumni CLI - Add to PATH
echo =======================
echo.

REM Check if Poetry is installed
poetry --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Poetry is not installed. Please install Poetry first.
    exit /b 1
)

REM Get Poetry environment path
for /f "tokens=*" %%i in ('poetry env info --path 2^>nul') do set POETRY_ENV=%%i

if "%POETRY_ENV%"=="" (
    echo ERROR: Poetry environment not found. Run 'poetry install' first.
    exit /b 1
)

set BIN_PATH=%POETRY_ENV%\Scripts

echo Poetry environment found: %POETRY_ENV%
echo Binary path: %BIN_PATH%
echo.

REM Check if already in PATH
echo %PATH% | findstr /C:"%BIN_PATH%" >nul
if not errorlevel 1 (
    echo Lumni CLI is already in your PATH!
    echo.
    echo Verify with: lumni --help
    exit /b 0
)

echo Adding to PATH for current session...
set PATH=%BIN_PATH%;%PATH%

echo.
echo PATH updated for current session.
echo.
echo To make this permanent, add this to your PATH environment variable:
echo   %BIN_PATH%
echo.
echo You can do this via:
echo   1. System Properties ^> Environment Variables
echo   2. Or run: setx PATH "%BIN_PATH%;%PATH%"
echo.
echo Then verify with: lumni --help

