@echo off
echo 🚀 Setting up Rossmann Sales Forecasting Website
echo ==================================================

REM Navigate to the website directory
cd /d "%~dp0"

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
) else (
    echo ✅ Node.js is installed
    node --version
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is not installed. Please install npm.
    pause
    exit /b 1
) else (
    echo ✅ npm is installed
    npm --version
)

REM Install dependencies
echo 📦 Installing dependencies...
npm install

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
) else (
    echo ✅ Dependencies installed successfully
)

REM Check if the API is running
echo 🔍 Checking if API is running on http://localhost:8000...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  API is not running on http://localhost:8000
    echo    Please start your FastAPI server first:
    echo    cd ../api ^&^& python main.py
) else (
    echo ✅ API is running and accessible
)

echo.
echo 🌐 Setup complete! To start the website:
echo    npm start
echo.
echo 📊 Then open your browser to: http://localhost:3000
echo 🔧 API should be running on: http://localhost:8000
echo.
echo Happy forecasting! 📈
pause
