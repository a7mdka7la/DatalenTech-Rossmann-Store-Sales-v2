@echo off
echo ========================================
echo Starting Rossmann Sales Forecasting Application
echo ========================================

echo.
echo Checking if required files exist...

if not exist "rossmann_random_forest_model.pkl" (
    echo Error: Model file not found! Please ensure rossmann_random_forest_model.pkl exists.
    pause
    exit /b 1
)

if not exist "api\main.py" (
    echo Error: API file not found! Please ensure api\main.py exists.
    pause
    exit /b 1
)

if not exist "website\server.js" (
    echo Error: Website server file not found! Please ensure website\server.js exists.
    pause
    exit /b 1
)

echo.
echo All required files found!
echo.

echo Installing Python dependencies for API...
cd api
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Error installing Python dependencies!
    pause
    exit /b 1
)

echo.
echo Installing Node.js dependencies for website...
cd ..\website
call npm install
if %ERRORLEVEL% neq 0 (
    echo Error installing Node.js dependencies!
    pause
    exit /b 1
)

echo.
echo Starting FastAPI server (Port 8000)...
cd ..\api
start "FastAPI Server" cmd /k "python main.py"

echo Waiting for API to start...
timeout /t 5 /nobreak >nul

echo.
echo Checking for existing processes on ports 8000 and 3000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing existing process on port 8000 (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    echo Killing existing process on port 3000 (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Starting Website server (Port 3001)...
cd ..\website
set PORT=3001
start "Website Server" cmd /k "set PORT=3001 && npm start"

echo.
echo ========================================
echo Application started successfully!
echo ========================================
echo.
echo FastAPI Server: http://localhost:8000
echo Website: http://localhost:3001
echo API Documentation: http://localhost:8000/docs
echo.
echo Press any key to return to command prompt...
pause >nul

cd ..
