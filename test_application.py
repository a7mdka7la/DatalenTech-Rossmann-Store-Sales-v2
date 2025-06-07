#!/usr/bin/env python3
"""
Test script for Rossmann Sales Forecasting API
Tests all API endpoints to ensure functionality
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 10

def test_api_health():
    """Test the health endpoint"""
    print("Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return data.get("model_loaded", False)
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_model_info():
    """Test the model info endpoint"""
    print("\nTesting model info...")
    try:
        response = requests.get(f"{API_BASE_URL}/model/info", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model info retrieved: {data['model_type']} with {data['total_features']} features")
            return True
        else:
            print(f"❌ Model info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model info error: {e}")
        return False

def test_single_prediction():
    """Test single prediction endpoint"""
    print("\nTesting single prediction...")
    
    # Test data
    test_data = {
        "store": 1,
        "date": "2024-01-15",
        "promo": 1,
        "state_holiday": "0",
        "school_holiday": 0
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict/simple",
            json=test_data,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Single prediction successful:")
            print(f"   Store {data['store']} on {data['date']}: ${data['forecasted_sales']:.2f}")
            return True
        else:
            print(f"❌ Single prediction failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Single prediction error: {e}")
        return False

def test_batch_prediction():
    """Test batch prediction endpoint"""
    print("\nTesting batch prediction...")
    
    # Test data for batch
    test_data = {
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
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict/batch/simple",
            json=test_data,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Batch prediction successful:")
            print(f"   Processed {data['total_predictions']} predictions")
            for pred in data['predictions'][:2]:  # Show first 2
                print(f"   Store {pred['store']}: ${pred['forecasted_sales']:.2f}")
            return True
        else:
            print(f"❌ Batch prediction failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Batch prediction error: {e}")
        return False

def test_website_availability():
    """Test if the website is accessible"""
    print("\nTesting website availability...")
    try:
        response = requests.get("http://localhost:3000", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            print("✅ Website is accessible at http://localhost:3000")
            return True
        else:
            print(f"❌ Website not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Website availability error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Rossmann API Tests")
    print("=" * 50)
    
    # Track test results
    results = []
    
    # Test API health
    model_loaded = test_api_health()
    results.append(("Health Check", model_loaded))
    
    if not model_loaded:
        print("\n❌ Model not loaded - skipping prediction tests")
        print("Make sure the model file 'rossmann_random_forest_model.pkl' exists")
        return False
    
    # Test model info
    results.append(("Model Info", test_model_info()))
    
    # Test predictions
    results.append(("Single Prediction", test_single_prediction()))
    results.append(("Batch Prediction", test_batch_prediction()))
    
    # Test website
    results.append(("Website", test_website_availability()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your application is ready to use.")
        print("📱 Open http://localhost:3000 to access the web interface")
        print("📖 API documentation: http://localhost:8000/docs")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
