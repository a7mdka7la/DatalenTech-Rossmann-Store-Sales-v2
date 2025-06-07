#!/bin/bash

echo "🚀 Setting up Rossmann Sales Forecasting Website"
echo "=================================================="

# Navigate to the website directory
cd "$(dirname "$0")"

# Check if Node.js is installed
if command -v node &> /dev/null; then
    echo "✅ Node.js is installed: $(node --version)"
else
    echo "❌ Node.js is not installed. Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if command -v npm &> /dev/null; then
    echo "✅ npm is installed: $(npm --version)"
else
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if the API is running
echo "🔍 Checking if API is running on http://localhost:8000..."
if curl -s http://localhost:8000/health &> /dev/null; then
    echo "✅ API is running and accessible"
else
    echo "⚠️  API is not running on http://localhost:8000"
    echo "   Please start your FastAPI server first:"
    echo "   cd ../api && python main.py"
fi

echo ""
echo "🌐 Setup complete! To start the website:"
echo "   npm start"
echo ""
echo "📊 Then open your browser to: http://localhost:3000"
echo "🔧 API should be running on: http://localhost:8000"
echo ""
echo "Happy forecasting! 📈"
