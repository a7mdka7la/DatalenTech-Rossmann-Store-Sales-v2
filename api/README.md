# Rossmann Sales Forecasting API

A FastAPI-based REST API for real-time deployment of the Rossmann sales forecasting model.

## Features

- 🚀 FastAPI with automatic OpenAPI/Swagger documentation
- 📊 Single and batch prediction endpoints
- 🔄 Model retraining endpoint
- 🐳 Docker containerization
- 📝 Comprehensive error handling and logging
- 💯 Input validation with Pydantic models
- 🏥 Health check endpoints

## Quick Start

### Prerequisites

- Python 3.9+
- Docker (optional)

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the API server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Swagger docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Deployment

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Or build and run manually:**
   ```bash
   docker build -t rossmann-api .
   docker run -p 8000:8000 -v $(pwd)/../rossmann_random_forest_model.pkl:/app/rossmann_random_forest_model.pkl -v $(pwd)/../feature_scaler.pkl:/app/feature_scaler.pkl rossmann-api
   ```

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /model/info` - Model information

### Prediction Endpoints

- `POST /predict` - Single prediction
- `POST /predict/batch` - Batch predictions

### Management Endpoints

- `POST /retrain` - Trigger model retraining

## Usage Examples

### Single Prediction

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "store": 1,
    "date": "2023-12-15",
    "promo": 1,
    "state_holiday": "0",
    "school_holiday": 0,
    "day_of_week": 5
  }'
```

### Batch Prediction

```bash
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "predictions": [
      {
        "store": 1,
        "date": "2023-12-15",
        "promo": 1,
        "state_holiday": "0",
        "school_holiday": 0,
        "day_of_week": 5
      },
      {
        "store": 2,
        "date": "2023-12-16",
        "promo": 0,
        "state_holiday": "0",
        "school_holiday": 0,
        "day_of_week": 6
      }
    ]
  }'
```

### Python Client Example

```python
import requests

# Single prediction
response = requests.post("http://localhost:8000/predict", json={
    "store": 1,
    "date": "2023-12-15",
    "promo": 1,
    "state_holiday": "0",
    "school_holiday": 0,
    "day_of_week": 5
})

print(response.json())
```

## Testing

Run the test suite:

```bash
python test_api.py
```

## Model Requirements

The API expects the following files in the parent directory:
- `rossmann_random_forest_model.pkl` - Trained Random Forest model
- `feature_scaler.pkl` - Feature scaler for preprocessing

## Input Schema

### PredictionRequest

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| store | int | Store ID | >= 1 |
| date | str | Date | YYYY-MM-DD format |
| promo | int | Promotion flag | 0 or 1 |
| state_holiday | str | State holiday | "0", "a", "b", or "c" |
| school_holiday | int | School holiday flag | 0 or 1 |
| day_of_week | int | Day of week | 1-7 |

## Output Schema

### PredictionResponse

| Field | Type | Description |
|-------|------|-------------|
| store | int | Store ID |
| date | str | Date |
| forecasted_sales | float | Predicted sales |
| confidence_score | float | Model confidence (0-1) |

## Deployment

### Free-tier Cloud Options

1. **Render.com** (Recommended)
   - Fork this repository
   - Connect to Render
   - Deploy as web service
   - Upload model files via dashboard

2. **Railway**
   - Connect GitHub repository
   - Deploy with auto-scaling
   - Configure environment variables

3. **Heroku**
   - Use buildpacks for Python
   - Store model files in S3
   - Configure dyno sizing

### Environment Variables

- `MODEL_PATH` - Path to model file (optional)
- `SCALER_PATH` - Path to scaler file (optional)
- `LOG_LEVEL` - Logging level (default: INFO)

## Architecture

```
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
├── test_api.py         # API test suite
└── README.md           # Documentation
```

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request** - Invalid input data
- **404 Not Found** - Endpoint not found
- **500 Internal Server Error** - Server errors
- **503 Service Unavailable** - Model not loaded

## Logging

The API logs important events:
- Model loading/reloading
- Prediction requests
- Error conditions
- Health checks

## Security Considerations

- Input validation with Pydantic
- CORS middleware configured
- Rate limiting (can be added)
- Authentication (can be added)

## Performance

- Async endpoints for scalability
- Background tasks for retraining
- Batch prediction support
- Health checks for monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Add tests
5. Submit a pull request

## License

MIT License
