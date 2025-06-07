import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://127.0.0.1:8000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_model_info():
    """Test model info endpoint"""
    print("Testing model info...")
    response = requests.get(f"{BASE_URL}/model/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_single_prediction():
    """Test single prediction endpoint"""
    print("Testing single prediction...")
    
    # Test data
    test_data = {
        "store": 1,
        "date": "2023-12-15",
        "promo": 1,
        "state_holiday": "0",
        "school_holiday": 0,
        "day_of_week": 5
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=test_data)
    print(f"Status: {response.status_code}")
    print(f"Request: {test_data}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_batch_prediction():
    """Test batch prediction endpoint"""
    print("Testing batch prediction...")
    
    # Create test data for multiple predictions
    predictions = []
    base_date = datetime(2023, 12, 15)
    
    for i in range(3):
        date = base_date + timedelta(days=i)
        predictions.append({
            "store": 1 + i,
            "date": date.strftime("%Y-%m-%d"),
            "promo": i % 2,
            "state_holiday": "0",
            "school_holiday": 0,
            "day_of_week": (5 + i) % 7 + 1
        })
    
    test_data = {"predictions": predictions}
    
    response = requests.post(f"{BASE_URL}/predict/batch", json=test_data)
    print(f"Status: {response.status_code}")
    print(f"Request: {len(predictions)} predictions")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_retrain():
    """Test retrain endpoint"""
    print("Testing retrain endpoint...")
    response = requests.post(f"{BASE_URL}/retrain")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_swagger_docs():
    """Test that Swagger docs are accessible"""
    print("Testing Swagger documentation...")
    response = requests.get(f"{BASE_URL}/docs")
    print(f"Swagger docs status: {response.status_code}")
    
    response = requests.get(f"{BASE_URL}/openapi.json")
    print(f"OpenAPI spec status: {response.status_code}")
    print("-" * 50)

if __name__ == "__main__":
    print("Starting API tests...")
    print("=" * 50)
    
    try:
        # Test all endpoints
        test_health_check()
        test_model_info()
        test_single_prediction()
        test_batch_prediction()
        test_retrain()
        test_swagger_docs()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error running tests: {str(e)}")
