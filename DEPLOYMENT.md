# Rossmann Sales Forecasting - Deployment Guide

## 🚀 Quick Start

### Step 1: Start the Application

**Windows (Easy Method):**
```bash
# Double-click the batch file or run in Command Prompt
start_application.bat
```

**Linux/MacOS:**
```bash
chmod +x start_application.sh
./start_application.sh
```

**Manual Method:**
```bash
# Terminal 1 - Start API
cd api
pip install -r requirements.txt
python main.py

# Terminal 2 - Start Website
cd website
npm install
npm start
```

### Step 2: Access the Application

- **Website**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

### Step 3: Test the Application

```bash
# Run automated tests
python test_application.py
```

## 📋 Prerequisites

1. **Python 3.8+** with pip installed
2. **Node.js 14+** with npm installed
3. **Model file**: `rossmann_random_forest_model.pkl` in root directory

## 🛠️ Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the ports
   netstat -ano | findstr :8000
   netstat -ano | findstr :3000
   
   # Kill processes if needed
   taskkill /PID <PID_NUMBER> /F
   ```

2. **Model Not Found**
   - Ensure `rossmann_random_forest_model.pkl` exists in the root directory
   - Run the Jupyter notebook to generate the model if missing

3. **Python Dependencies**
   ```bash
   cd api
   pip install -r requirements.txt
   ```

4. **Node.js Dependencies**
   ```bash
   cd website
   npm install
   ```

### Environment Variables

Create `.env` files if needed:

**API (.env in api/ folder):**
```
MODEL_PATH=../rossmann_random_forest_model.pkl
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

**Website (.env in website/ folder):**
```
NODE_ENV=development
PORT=3000
API_URL=http://localhost:8000
```

## 🌐 Production Deployment

### Option 1: Docker Deployment

```bash
# Build and run API
cd api
docker build -t rossmann-api .
docker run -p 8000:8000 rossmann-api

# Build and run Website
cd website
docker build -t rossmann-website .
docker run -p 3000:3000 rossmann-website
```

### Option 2: Cloud Deployment

**Railway:**
1. Push code to GitHub
2. Connect Railway to your repository
3. Deploy both api/ and website/ as separate services

**Heroku:**
1. Create two apps (api and website)
2. Deploy using Git push
3. Set environment variables in Heroku dashboard

**Render:**
1. Connect GitHub repository
2. Create web services for both components
3. Configure build commands and environment variables

## 📊 Usage Examples

### Single Prediction (Web Interface)

1. Open http://localhost:3000
2. Fill the form:
   - Store ID: 1
   - Date: 2024-01-15
   - Promotion: Yes
   - State Holiday: No Holiday
   - School Holiday: No
3. Click "Get Prediction"

### Batch Prediction (Web Interface)

1. Click "Add Prediction" multiple times
2. Fill each form with different parameters
3. Click "Run Batch Prediction"
4. Download results as CSV

### API Usage (curl)

```bash
# Single prediction
curl -X POST "http://localhost:8000/predict/simple" \
  -H "Content-Type: application/json" \
  -d '{
    "store": 1,
    "date": "2024-01-15",
    "promo": 1,
    "state_holiday": "0",
    "school_holiday": 0
  }'

# Batch prediction
curl -X POST "http://localhost:8000/predict/batch/simple" \
  -H "Content-Type: application/json" \
  -d '{
    "predictions": [
      {
        "store": 1,
        "date": "2024-01-15",
        "promo": 1,
        "state_holiday": "0",
        "school_holiday": 0
      },
      {
        "store": 2,
        "date": "2024-01-16",
        "promo": 0,
        "state_holiday": "0",
        "school_holiday": 1
      }
    ]
  }'
```

## 🔧 Development

### Hot Reload Development

```bash
# API with auto-reload
cd api
pip install uvicorn[standard]
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Website with auto-reload
cd website
npm run dev
```

### Adding New Features

1. **API**: Modify `api/main.py`
2. **Website**: Update `website/script.js` and `website/index.html`
3. **Styling**: Edit `website/styles.css`

### Testing

```bash
# Test API
python test_application.py

# Test individual endpoints
python api/test_api.py

# Manual testing
# Open http://localhost:3000 and test the interface
```

## 📈 Monitoring

### Health Checks

- API Health: http://localhost:8000/health
- Website Health: http://localhost:3000/health

### Logs

- API logs: Check terminal where `python main.py` is running
- Website logs: Check terminal where `npm start` is running

### Performance

- API response times: Check FastAPI docs at http://localhost:8000/docs
- Model prediction time: Usually < 100ms per prediction

## 🔒 Security Notes

### For Production:

1. **Environment Variables**: Never commit secrets to Git
2. **CORS**: Update CORS settings for your domain
3. **HTTPS**: Use SSL/TLS certificates
4. **Rate Limiting**: Implement API rate limiting
5. **Authentication**: Add user authentication if needed

### Example Production Settings:

```python
# api/main.py - Production CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 📞 Support

- 📧 Email: support@datalentech.com
- 🐛 Issues: Create GitHub issues
- 📖 Documentation: http://localhost:8000/docs

---

**Happy Forecasting! 🎯**
