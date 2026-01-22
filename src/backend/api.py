from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

script_dir = Path(__file__).parent
data_path = script_dir.parent.parent / "data" / "taxi_trip_clean.csv"
model_path = script_dir.parent / "model_development" / "taxi_price_model.pkl" 

# AI-assisted code: My original try-except structure was modified by the AI
try:
    df = pd.read_csv(data_path)
except FileNotFoundError:
    print(f"ERROR: Could not find the CSV file at path: {data_path}")
    df = None

try:
    pipeline = joblib.load(model_path)
    print("INFO: Model file loaded successfully.") 
except FileNotFoundError:
    print(f"ERROR: Could not find the model file at path: {model_path}")
    pipeline = None


class TripFeatures(BaseModel):
    Trip_Distance_km: float
    Passenger_Count: int
    Base_Fare: float
    Per_Km_Rate: float
    Per_Minute_Rate: float
    Trip_Duration_Minutes: float

app = FastAPI(
    title="Taxi Price Prediction API",
    description="An API to predict taxi prices and serve training data.",
    version="1.1"
)

@app.get("/")
def root():
    return {"message": "Welcome to the Taxi Price Prediction API"}

@app.get("/data/head")
def get_data_head(n: int = 10):
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset file not found.")
    
    return df.head(n).replace({np.nan: None}).to_dict(orient="records")

@app.get("/data/trip/{trip_id}")
def get_trip_by_id(trip_id: int):
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset file not found.")
    
    if trip_id not in df.index:
        raise HTTPException(status_code=404, detail=f"Trip with ID {trip_id} not found.")
        
    return df.loc[trip_id].replace({np.nan: None}).to_dict()

@app.post("/predict")
def predict(features: TripFeatures):
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline could not be loaded. Check API server logs for errors.")

    input_dict = features.dict()
    input_data = pd.DataFrame([input_dict])
    
    training_columns = [
        'Trip_Distance_km', 
        'Passenger_Count', 
        'Base_Fare', 
        'Per_Km_Rate', 
        'Per_Minute_Rate', 
        'Trip_Duration_Minutes'
    ]
    input_data = input_data[training_columns]

    prediction = pipeline.predict(input_data)[0]

    return {"predicted_price": round(prediction, 2)}