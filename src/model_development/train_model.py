"""Train, evaluate and export the taxi price prediction pipeline.

Run from the repository root:
    python -m src.model_development.train_model
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "taxi_trip_clean.csv"
MODEL_PATH = Path(__file__).resolve().parent / "taxi_price_model.pkl"
METADATA_PATH = Path(__file__).resolve().parent / "model_metadata.json"

FEATURES = [
    "Trip_Distance_km",
    "Passenger_Count",
    "Base_Fare",
    "Per_Km_Rate",
    "Per_Minute_Rate",
    "Trip_Duration_Minutes",
]
TARGET = "Trip_Price"


def make_pipeline(regressor):
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="mean")),
            ("regressor", regressor),
        ]
    )


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Training dataset not found: {DATA_PATH}")

    data = pd.read_csv(DATA_PATH)
    missing = [column for column in FEATURES + [TARGET] if column not in data.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    X = data[FEATURES]
    y = data[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    candidates = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(random_state=42),
        "Random Forest": RandomForestRegressor(random_state=42),
    }

    scores = {}
    for name, estimator in candidates.items():
        candidate = make_pipeline(estimator)
        candidate.fit(X_train, y_train)
        predictions = candidate.predict(X_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
        scores[name] = rmse
        print(f"{name} RMSE: {rmse:.4f}")

    best_name = min(scores, key=scores.get)
    best_pipeline = make_pipeline(candidates[best_name])
    best_pipeline.fit(X, y)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, MODEL_PATH)

    metadata = {
        "model": best_name,
        "target": TARGET,
        "features": FEATURES,
        "test_rmse": scores[best_name],
        "candidate_rmse": scores,
        "python_sklearn_version": sklearn.__version__,
        "training_rows": int(len(data)),
        "test_size": 0.2,
        "random_state": 42,
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    # Verify that the exported artifact can be loaded and predicts with the API schema.
    loaded_pipeline = joblib.load(MODEL_PATH)
    sample_prediction = float(loaded_pipeline.predict(X.iloc[[0]])[0])
    print(f"Saved model: {MODEL_PATH}")
    print(f"Saved metadata: {METADATA_PATH}")
    print(f"Artifact smoke test prediction: {sample_prediction:.2f}")


if __name__ == "__main__":
    main()
