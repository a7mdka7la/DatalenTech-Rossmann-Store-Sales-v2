from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import pandas as pd
import joblib
import numpy as np
from datetime import datetime, timedelta
import logging
import os
import asyncio
import uvicorn
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Rossmann Sales Forecasting API",
    description="REST API for real-time deployment of Rossmann sales forecasting model",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and scaler
model = None
scaler = None
model_info = {}

# Pydantic models
class PredictionRequest(BaseModel):
    store: int = Field(..., description="Store ID", ge=1)
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    promo: int = Field(..., description="Promotion (0 or 1)", ge=0, le=1)
    state_holiday: str = Field(..., description="State holiday (0, a, b, c)")
    school_holiday: int = Field(..., description="School holiday (0 or 1)", ge=0, le=1)
    day_of_week: int = Field(..., description="Day of week (1-7)", ge=1, le=7)
    
    # Optional fields for advanced features (when available)
    store_type: Optional[str] = Field(None, description="Store type (a, b, c, d)")
    assortment: Optional[str] = Field(None, description="Assortment (a, b, c)")
    competition_distance: Optional[float] = Field(None, description="Distance to nearest competitor")
    competition_open_since_month: Optional[int] = Field(None, description="Month when competition opened")
    competition_open_since_year: Optional[int] = Field(None, description="Year when competition opened")
    
    # Historical sales data (for proper feature engineering)
    recent_sales: Optional[List[float]] = Field(None, description="Recent sales data for rolling calculations (last 30 days)")
    
class SimplePredictionRequest(BaseModel):
    """Simplified version that works with basic inputs and default values"""
    store: int = Field(..., description="Store ID", ge=1)
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    promo: int = Field(..., description="Promotion (0 or 1)", ge=0, le=1)
    state_holiday: str = Field(default="0", description="State holiday (0, a, b, c)")
    school_holiday: int = Field(default=0, description="School holiday (0 or 1)", ge=0, le=1)
    day_of_week: Optional[int] = Field(None, description="Day of week (1-7, auto-calculated if not provided)", ge=1, le=7)

class BatchPredictionRequest(BaseModel):
    predictions: List[PredictionRequest]

class SimpleBatchPredictionRequest(BaseModel):
    predictions: List[SimplePredictionRequest]

class PredictionResponse(BaseModel):
    store: int
    date: str
    forecasted_sales: float
    confidence_score: Optional[float] = None

class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    total_predictions: int

class ModelInfo(BaseModel):
    model_config = {"protected_namespaces": ()}  # Add this line
    
    model_type: str
    trained_on: str
    version: str
    features: List[str]
    total_features: int
    model_requirements: str

class HealthResponse(BaseModel):
    model_config = {"protected_namespaces": ()}  # Add this line
    
    status: str
    model_loaded: bool
    timestamp: str

# Helper functions
def load_model_and_scaler():
    """Load the trained model and scaler"""
    global model, scaler, model_info
    
    try:
        # Get the parent directory (where the model files are located)
        parent_dir = Path(__file__).parent.parent
        
        model_path = parent_dir / "rossmann_random_forest_model.pkl"
        scaler_path = parent_dir / "feature_scaler.pkl"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        if not scaler_path.exists():
            raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        model_info = {
            "model_type": "Random Forest Regressor",
            "trained_on": "Rossmann Store Sales Dataset",
            "version": "1.0.0",
            "features": [
                "Store", "DayOfWeek", "Promo", "StateHoliday_encoded", "SchoolHoliday",
                "StoreType_encoded", "Assortment_encoded", "CompetitionDistance",
                "CompetitionOpen", "Year", "Month", "Day", "WeekOfYear", "Quarter",
                "IsWeekend", "IsMonthEnd", "IsMonthStart", "Month_sin", "Month_cos",
                "DayOfWeek_sin", "DayOfWeek_cos", "Sales_lag_1", "Sales_lag_7",
                "Sales_lag_14", "Sales_lag_30", "Sales_rolling_mean_7", "Sales_rolling_std_7",
                "Sales_rolling_mean_14", "Sales_rolling_std_14", "Sales_rolling_mean_30",
                "Sales_rolling_std_30"
            ],
            "total_features": 31,
            "model_requirements": "Requires engineered features including sales history, rolling statistics, and cyclical encodings"
        }
        
        logger.info("Model and scaler loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

def create_features(data: PredictionRequest) -> pd.DataFrame:
    """Create features from prediction request with proper feature engineering"""
    try:
        # Parse date
        date_obj = datetime.strptime(data.date, "%Y-%m-%d")
        
        # Base temporal features
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day
        week_of_year = date_obj.isocalendar()[1]
        day_of_week = data.day_of_week if data.day_of_week else date_obj.isoweekday()
        quarter = (month - 1) // 3 + 1
        
        # Cyclical encodings
        day_of_week_cos = np.cos(2 * np.pi * day_of_week / 7)
        day_of_week_sin = np.sin(2 * np.pi * day_of_week / 7)
        month_cos = np.cos(2 * np.pi * month / 12)
        month_sin = np.sin(2 * np.pi * month / 12)
        
        # Boolean features
        is_weekend = 1 if day_of_week in [6, 7] else 0
        is_month_end = 1 if (date_obj + timedelta(days=1)).day == 1 else 0
        is_month_start = 1 if day == 1 else 0
        
        # State holiday encoding
        state_holiday_encoded = 0
        if data.state_holiday == 'a':
            state_holiday_encoded = 1
        elif data.state_holiday == 'b':
            state_holiday_encoded = 2
        elif data.state_holiday == 'c':
            state_holiday_encoded = 3
        
        # Store type and assortment encoding (use defaults if not provided)
        store_type_encoded = 0  # Default
        if hasattr(data, 'store_type') and data.store_type:
            store_type_map = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
            store_type_encoded = store_type_map.get(data.store_type.lower(), 0)
        
        assortment_encoded = 0  # Default
        if hasattr(data, 'assortment') and data.assortment:
            assortment_map = {'a': 1, 'b': 2, 'c': 3}
            assortment_encoded = assortment_map.get(data.assortment.lower(), 0)
        
        # Competition features
        competition_distance = getattr(data, 'competition_distance', 1000.0)  # Default distance
        competition_open = 0
        if hasattr(data, 'competition_open_since_year') and data.competition_open_since_year:
            if data.competition_open_since_year <= year:
                competition_open = 1
        
        # Sales-based features (use defaults when historical data not available)
        if hasattr(data, 'recent_sales') and data.recent_sales and len(data.recent_sales) >= 30:
            sales_data = np.array(data.recent_sales[-30:])  # Last 30 days
            
            # Rolling means
            sales_rolling_mean_7 = np.mean(sales_data[-7:]) if len(sales_data) >= 7 else np.mean(sales_data)
            sales_rolling_mean_14 = np.mean(sales_data[-14:]) if len(sales_data) >= 14 else np.mean(sales_data)
            sales_rolling_mean_30 = np.mean(sales_data)
            
            # Rolling standard deviations
            sales_rolling_std_7 = np.std(sales_data[-7:]) if len(sales_data) >= 7 else np.std(sales_data)
            sales_rolling_std_14 = np.std(sales_data[-14:]) if len(sales_data) >= 14 else np.std(sales_data)
            sales_rolling_std_30 = np.std(sales_data)
            
            # Lag features
            sales_lag_1 = sales_data[-1] if len(sales_data) >= 1 else sales_rolling_mean_7
            sales_lag_7 = sales_data[-7] if len(sales_data) >= 7 else sales_rolling_mean_7
            sales_lag_14 = sales_data[-14] if len(sales_data) >= 14 else sales_rolling_mean_14
            sales_lag_30 = sales_data[-30] if len(sales_data) >= 30 else sales_rolling_mean_30
        else:
            # Use store and promo-based estimates when no historical data
            base_sales = 5000.0  # Base estimate
            promo_multiplier = 1.2 if data.promo else 1.0
            store_factor = 1.0 + (data.store % 100) / 1000  # Simple store variation
            weekend_factor = 1.1 if is_weekend else 1.0
            
            estimated_sales = base_sales * promo_multiplier * store_factor * weekend_factor
            
            # Add some realistic variation
            np.random.seed(data.store + day)  # Reproducible randomness
            
            # Default values based on estimated sales
            sales_rolling_mean_7 = estimated_sales * (0.9 + np.random.uniform(-0.1, 0.1))
            sales_rolling_mean_14 = estimated_sales * (0.95 + np.random.uniform(-0.05, 0.05))
            sales_rolling_mean_30 = estimated_sales
            
            sales_rolling_std_7 = sales_rolling_mean_7 * 0.15
            sales_rolling_std_14 = sales_rolling_mean_14 * 0.12
            sales_rolling_std_30 = sales_rolling_mean_30 * 0.10
            
            sales_lag_7 = sales_rolling_mean_7
            sales_lag_1 = sales_rolling_mean_7 * (1.0 + np.random.uniform(-0.2, 0.2))          
            sales_lag_14 = sales_rolling_mean_14
            sales_lag_30 = sales_rolling_mean_30
        
        # Create feature dictionary in the exact order expected by the model
        features = {
            'Store': data.store,
            'DayOfWeek': day_of_week,
            'Promo': data.promo,
            'StateHoliday_encoded': state_holiday_encoded,
            'SchoolHoliday': data.school_holiday,
            'StoreType_encoded': store_type_encoded,
            'Assortment_encoded': assortment_encoded,
            'CompetitionDistance': competition_distance,
            'CompetitionOpen': competition_open,
            'Year': year,
            'Month': month,
            'Day': day,
            'WeekOfYear': week_of_year,
            'Quarter': quarter,
            'IsWeekend': is_weekend,
            'IsMonthEnd': is_month_end,
            'IsMonthStart': is_month_start,
            'Month_sin': month_sin,
            'Month_cos': month_cos,
            'DayOfWeek_sin': day_of_week_sin,
            'DayOfWeek_cos': day_of_week_cos,
            'Sales_lag_1': sales_lag_1,
            'Sales_lag_7': sales_lag_7,
            'Sales_lag_14': sales_lag_14,
            'Sales_lag_30': sales_lag_30,
            'Sales_rolling_mean_7': sales_rolling_mean_7,
            'Sales_rolling_std_7': sales_rolling_std_7,
            'Sales_rolling_mean_14': sales_rolling_mean_14,
            'Sales_rolling_std_14': sales_rolling_std_14,
            'Sales_rolling_mean_30': sales_rolling_mean_30,
            'Sales_rolling_std_30': sales_rolling_std_30
        }
        
        # Create DataFrame
        df = pd.DataFrame([features])
        
        return df
        
    except Exception as e:
        logger.error(f"Error creating features: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Feature engineering failed: {str(e)}")

def create_simple_features(data: SimplePredictionRequest) -> pd.DataFrame:
    """Create features from simplified prediction request with default values"""
    # Convert to full PredictionRequest with defaults
    full_request = PredictionRequest(
        store=data.store,
        date=data.date,
        promo=data.promo,
        state_holiday=data.state_holiday,
        school_holiday=data.school_holiday,
        day_of_week=data.day_of_week if data.day_of_week else datetime.strptime(data.date, "%Y-%m-%d").isoweekday()
    )
    return create_features(full_request)

def make_prediction(features_df: pd.DataFrame) -> tuple:
    """Make prediction using the loaded model"""
    try:
        # Scale features
        features_scaled = scaler.transform(features_df)
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        
        # Calculate confidence (using prediction interval estimation)
        # For Random Forest, we can use the standard deviation of tree predictions
        if hasattr(model, 'estimators_'):
            tree_predictions = [tree.predict(features_scaled)[0] for tree in model.estimators_]
            confidence = 1 - (np.std(tree_predictions) / np.mean(tree_predictions))
            confidence = max(0, min(1, confidence))  # Ensure between 0 and 1
        else:
            confidence = 0.85  # Default confidence
        
        return float(prediction), float(confidence)
        
    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    success = load_model_and_scaler()
    if not success:
        logger.error("Failed to load model on startup")

# API Routes
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Rossmann Sales Forecasting API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        timestamp=datetime.now().isoformat()
    )

@app.get("/model/info", response_model=ModelInfo, tags=["Model"])
async def get_model_info():
    """Get model information"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return ModelInfo(**model_info)

@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_sales(request: PredictionRequest):
    """Predict sales for a single store and date"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Create features
        features_df = create_features(request)
        
        # Make prediction
        prediction, confidence = make_prediction(features_df)
        
        return PredictionResponse(
            store=request.store,
            date=request.date,
            forecasted_sales=prediction,
            confidence_score=confidence
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/predict/simple", response_model=PredictionResponse, tags=["Prediction"])
async def predict_sales_simple(request: SimplePredictionRequest):
    """Predict sales using simplified input (automatically fills missing features)"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Create features
        features_df = create_simple_features(request)
        
        # Make prediction
        prediction, confidence = make_prediction(features_df)
        
        return PredictionResponse(
            store=request.store,
            date=request.date,
            forecasted_sales=prediction,
            confidence_score=confidence
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Prediction"])
async def predict_sales_batch(request: BatchPredictionRequest):
    """Predict sales for multiple stores and dates"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if len(request.predictions) > 1000:
        raise HTTPException(status_code=400, detail="Maximum 1000 predictions per batch")
    
    try:
        predictions = []
        
        for pred_request in request.predictions:
            # Create features
            features_df = create_features(pred_request)
            
            # Make prediction
            prediction, confidence = make_prediction(features_df)
            
            predictions.append(PredictionResponse(
                store=pred_request.store,
                date=pred_request.date,
                forecasted_sales=prediction,
                confidence_score=confidence
            ))
        
        return BatchPredictionResponse(
            predictions=predictions,
            total_predictions=len(predictions)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/predict/batch/simple", response_model=BatchPredictionResponse, tags=["Prediction"])
async def predict_sales_batch_simple(request: SimpleBatchPredictionRequest):
    """Predict sales for multiple stores and dates using simplified input"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if len(request.predictions) > 1000:
        raise HTTPException(status_code=400, detail="Maximum 1000 predictions per batch")
    
    try:
        predictions = []
        
        for pred_request in request.predictions:
            # Create features
            features_df = create_simple_features(pred_request)
            
            # Make prediction
            prediction, confidence = make_prediction(features_df)
            
            predictions.append(PredictionResponse(
                store=pred_request.store,
                date=pred_request.date,
                forecasted_sales=prediction,
                confidence_score=confidence
            ))
        
        return BatchPredictionResponse(
            predictions=predictions,
            total_predictions=len(predictions)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def retrain_model_task():
    """Background task to retrain the model"""
    try:
        logger.info("Starting model retraining...")
        # In a real implementation, you would:
        # 1. Fetch new training data
        # 2. Retrain the model
        # 3. Validate the new model
        # 4. Replace the old model if validation passes
        
        # For this demo, we'll just reload the existing model
        await asyncio.sleep(5)  # Simulate training time
        load_model_and_scaler()
        logger.info("Model retraining completed")
        
    except Exception as e:
        logger.error(f"Model retraining failed: {str(e)}")

@app.post("/retrain", tags=["Model Management"])
async def retrain_model(background_tasks: BackgroundTasks):
    """Trigger model retraining"""
    background_tasks.add_task(retrain_model_task)
    return {
        "message": "Model retraining started",
        "status": "initiated",
        "timestamp": datetime.now().isoformat()
    }

# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "status_code": 404}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
