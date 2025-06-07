# Rossmann Sales Forecasting Web Application

A complete machine learning web application for predicting Rossmann store sales using FastAPI and a modern web interface.

## Features

- **Single Store Prediction**: Get instant sales forecasts for individual stores
- **Batch Predictions**: Process multiple predictions simultaneously
- **Real-time Model Status**: Monitor API health and model availability
- **Interactive Visualizations**: View prediction results with confidence scores
- **Model Information**: Detailed insights about the trained model
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │◄──►│   Express.js    │◄──►│   FastAPI       │
│   (HTML/CSS/JS) │    │   Server        │    │   Backend       │
│                 │    │   Port: 3001    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                               ┌─────────────────┐
                                               │   ML Model      │
                                               │   (Random       │
                                               │   Forest)       │
                                               └─────────────────┘
```

## Prerequisites

- **Python 3.8+** with pip
- **Node.js 14+** with npm
- **Git** (optional, for cloning)

## Quick Start

### Option 1: Automated Setup (Recommended)

**For Windows:**
```bash
# Simply run the batch file
start_application.bat
```

**For Linux/MacOS:**
```bash
# Make the script executable and run
chmod +x start_application.sh
./start_application.sh
```

### Option 2: Manual Setup

1. **Start the FastAPI Backend:**
```bash
cd api
pip install -r requirements.txt
python main.py
```

2. **Start the Web Frontend:**
```bash
cd website
npm install
npm start
```

3. **Access the Application:**
- Website: http://localhost:3001
- API Documentation: http://localhost:8000/docs
- API Health: http://localhost:8000/health

## Usage Guide

### Single Prediction

1. Navigate to http://localhost:3001
2. Fill in the prediction form:
   - **Store ID**: Enter a store number (1-1115)
   - **Date**: Select the prediction date
   - **Promotion**: Choose if promotion is active (0 or 1)
   - **State Holiday**: Select holiday type (0, a, b, c)
   - **School Holiday**: Choose if school holiday (0 or 1)
3. Click "Get Prediction"
4. View the forecasted sales and confidence score

### Batch Predictions

1. Click "Add Prediction" to create multiple prediction requests
2. Fill in details for each prediction
3. Click "Run Batch Prediction"
4. Export results as CSV if needed

## 🔌 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check API health and model status |
| GET | `/model/info` | Get model information and features |
| POST | `/predict` | Single prediction with full features |
| POST | `/predict/simple` | Simplified single prediction |
| POST | `/predict/batch` | Batch predictions |
| POST | `/predict/batch/simple` | Simplified batch predictions |

### Example API Request

```bash
curl -X POST "http://localhost:8000/predict/simple" \
     -H "Content-Type: application/json" \
     -d '{
       "store": 1,
       "date": "2024-01-15",
       "promo": 1,
       "state_holiday": "0",
       "school_holiday": 0
     }'
```

### Example Response

```json
{
  "store": 1,
  "date": "2024-01-15",
  "forecasted_sales": 7583.42,
  "confidence_score": 0.87
}
```

## 🛠️ Development

### Project Structure

```
rossmann-forecasting/
├── api/                          # FastAPI backend
│   ├── main.py                  # Main API application
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # Docker configuration
│   └── test_api.py             # API tests
├── website/                     # Web frontend
│   ├── index.html              # Main webpage
│   ├── script.js               # JavaScript functionality
│   ├── styles.css              # CSS styling
│   ├── server.js               # Express.js server
│   └── package.json            # Node.js dependencies
├── *.pkl                       # Trained ML models
├── *.csv                       # Data files and results
└── start_application.*         # Startup scripts
```

### Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
MODEL_PATH=../rossmann_random_forest_model.pkl

# Website Configuration
NODE_ENV=development
WEBSITE_PORT=3001
```

### Running Tests

```bash
# Test the API
cd api
python test_api.py

# Test the website (manual testing)
cd website
npm start
# Navigate to http://localhost:3001
```

## Docker Deployment

### Build and Run API

```bash
cd api
docker build -t rossmann-api .
docker run -p 8000:8000 rossmann-api
```

### Docker Compose (Full Stack)

```bash
docker-compose up -d
```

## Production Deployment

### Platform Options

1. **Heroku**: Use the included `railway.toml`
2. **Railway**: Ready-to-deploy configuration
3. **Render**: Use `render.yaml` configuration
4. **AWS/Azure/GCP**: Standard container deployment

### Environment Setup

1. Update API URLs in `website/script.js`
2. Set production environment variables
3. Configure CORS settings for your domain
4. Set up SSL/TLS certificates

## Model Information

- **Algorithm**: Random Forest Regressor
- **Features**: 27 engineered features including:
  - Temporal features (day, month, year, etc.)
  - Store characteristics
  - Promotional indicators
  - Lag and rolling statistics
  - Cyclical encodings
- **Performance**: 
  - RMSE: ~1,000-2,000 (depending on data)
  - MAPE: ~10-15%
  - R²: ~0.85-0.90

## Troubleshooting

### Common Issues

1. **Model not loading**:
   - Ensure `rossmann_random_forest_model.pkl` exists in root directory
   - Check Python version compatibility (3.8+)

2. **API connection failed**:
   - Verify FastAPI server is running on port 8000
   - Check firewall settings
   - Ensure CORS is properly configured

3. **Website not loading**:
   - Confirm Node.js server is running on port 3001
   - Check for port conflicts
   - Verify all npm dependencies are installed

4. **Prediction errors**:
   - Validate input data format
   - Check date format (YYYY-MM-DD)
   - Ensure store ID is within valid range

### Debug Mode

```bash
# Enable debug logging for API
export LOG_LEVEL=DEBUG
python api/main.py

# Enable development mode for website
export NODE_ENV=development
npm run dev
```



