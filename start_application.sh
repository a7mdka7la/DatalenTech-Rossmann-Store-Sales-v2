#!/bin/bash

echo "========================================"
echo "Starting Rossmann Sales Forecasting Application"
echo "========================================"

echo ""
echo "Checking if required files exist..."

if [ ! -f "rossmann_random_forest_model.pkl" ]; then
    echo "Error: Model file not found! Please ensure rossmann_random_forest_model.pkl exists."
    exit 1
fi

if [ ! -f "api/main.py" ]; then
    echo "Error: API file not found! Please ensure api/main.py exists."
    exit 1
fi

if [ ! -f "website/server.js" ]; then
    echo "Error: Website server file not found! Please ensure website/server.js exists."
    exit 1
fi

echo ""
echo "All required files found!"
echo ""

echo "Installing Python dependencies for API..."
cd api
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error installing Python dependencies!"
    exit 1
fi

echo ""
echo "Installing Node.js dependencies for website..."
cd ../website
npm install
if [ $? -ne 0 ]; then
    echo "Error installing Node.js dependencies!"
    exit 1
fi

echo ""
echo "Starting FastAPI server (Port 8000)..."
cd ../api
python main.py &
API_PID=$!

echo "Waiting for API to start..."
sleep 5

echo ""
echo "Starting Website server (Port 3000)..."
cd ../website
npm start &
WEBSITE_PID=$!

echo ""
echo "========================================"
echo "Application started successfully!"
echo "========================================"
echo ""
echo "FastAPI Server: http://localhost:8000"
echo "Website: http://localhost:3000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $API_PID 2>/dev/null
    kill $WEBSITE_PID 2>/dev/null
    echo "Services stopped."
    exit 0
}

# Trap the cleanup function to run on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait
