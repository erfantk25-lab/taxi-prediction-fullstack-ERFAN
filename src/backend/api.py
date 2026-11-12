from pathlib import Path
import warnings

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sklearn.exceptions import InconsistentVersionWarning

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "taxi_trip_clean.csv"
MODEL_PATH = BASE_DIR / "src" / "model_development" / "taxi_price_model.pkl"

FEATURES = [
    "Trip_Distance_km",
    "Passenger_Count",
    "Base_Fare",
    "Per_Km_Rate",
    "Per_Minute_Rate",
    "Trip_Duration_Minutes",
]

df = None
model = None

try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    print(f"WARNING: Dataset not found: {DATA_PATH}")

try:
    # joblib uses pickle internally. Only load model artifacts from this trusted repo.
    with warnings.catch_warnings():
        warnings.simplefilter("error", InconsistentVersionWarning)
        model = joblib.load(MODEL_PATH)

    model_features = list(getattr(model, "feature_names_in_", []))
    if model_features and model_features != FEATURES:
        raise ValueError(
            "Model feature order does not match API input schema. "
            f"Expected {FEATURES}, got {model_features}"
        )

    print(f"INFO: Model loaded successfully from {MODEL_PATH}")
except FileNotFoundError:
    print(f"ERROR: Model file not found: {MODEL_PATH}")
except Exception as exc:
    print(f"ERROR: Could not load model artifact: {exc}")
    model = None


class TripFeatures(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "Trip_Distance_km": 10.5,
                "Passenger_Count": 1,
                "Base_Fare": 50.0,
                "Per_Km_Rate": 18.0,
                "Per_Minute_Rate": 7.0,
                "Trip_Duration_Minutes": 15.0,
            }
        }
    )

    Trip_Distance_km: float
    Passenger_Count: int
    Base_Fare: float
    Per_Km_Rate: float
    Per_Minute_Rate: float
    Trip_Duration_Minutes: float


app = FastAPI(
    title="Taxi Price Prediction API",
    description="Predict taxi trip prices and inspect the cleaned training dataset.",
    version="1.2.0",
)


@app.get("/")
def root():
    return {"message": "Welcome to the Taxi Price Prediction API"}


@app.get("/health")
def health():
    return {
        "status": "ok" if model is not None else "degraded",
        "model_loaded": model is not None,
        "dataset_loaded": df is not None,
    }


@app.get("/data/head")
def get_data_head(n: int = 10):
    if df is None:
        raise HTTPException(status_code=503, detail="Dataset is not available.")
    if not 1 <= n <= 500:
        raise HTTPException(status_code=422, detail="n must be between 1 and 500.")
    return df.head(n).replace({np.nan: None}).to_dict(orient="records")


@app.get("/data/trip/{trip_id}")
def get_trip_by_id(trip_id: int):
    if df is None:
        raise HTTPException(status_code=503, detail="Dataset is not available.")
    if trip_id not in df.index:
        raise HTTPException(status_code=404, detail=f"Trip with ID {trip_id} not found.")
    return df.loc[trip_id].replace({np.nan: None}).to_dict()


@app.post("/predict")
def predict(features: TripFeatures):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is unavailable. Run the training script and restart the API.",
        )

    input_data = pd.DataFrame([features.model_dump()], columns=FEATURES)
    try:
        prediction = float(model.predict(input_data)[0])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc

    return {"predicted_price": round(prediction, 2)}
