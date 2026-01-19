# Fil: src/backend/api.py

# 1. Importera nödvändiga bibliotek
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np # <-- VIKTIGT: Importera numpy

# 2. Ladda in det rena datasetet
try:
    df = pd.read_csv("data/taxi_trip_clean.csv")
except FileNotFoundError:
    df = None

# 3. Definiera Pydantic-modell för prediktions-indata
class TripFeatures(BaseModel):
    Trip_Distance_km: float
    Passenger_Count: int
    Base_Fare: float
    Per_Km_Rate: float
    Per_Minute_Rate: float
    Trip_Duration_Minutes: float

# 4. Ladda den tränade pipelinen
try:
    pipeline = joblib.load("src/model_development/taxi_price_pipeline.pkl")
except FileNotFoundError:
    pipeline = None 

# 5. Skapa FastAPI-appen
app = FastAPI(
    title="Taxi Price Prediction API",
    description="Ett API för att förutsäga taxipriser och servera träningsdata.",
    version="1.1"
)

# 6. Endpoints
@app.get("/")
def root():
    return {"message": "Welcome to the Taxi Price Prediction API"}

@app.get("/data/head")
def get_data_head(n: int = 10):
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset file not found.")
    
    # NY RAD: Ersätt NaN med None, som är JSON-kompatibelt (blir null)
    return df.head(n).replace({np.nan: None}).to_dict(orient="records")

@app.get("/data/trip/{trip_id}")
def get_trip_by_id(trip_id: int):
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset file not found.")
    
    if trip_id not in df.index:
        raise HTTPException(status_code=404, detail=f"Trip with ID {trip_id} not found.")
        
    # NY RAD: Ersätt NaN med None även här
    return df.loc[trip_id].replace({np.nan: None}).to_dict()

@app.post("/predict")
def predict(features: TripFeatures):
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline could not be loaded.")

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