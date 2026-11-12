from fastapi.testclient import TestClient

from src.backend.api import app

client = TestClient(app)


def test_health_reports_loaded_model_and_dataset():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True
    assert body["dataset_loaded"] is True


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_prediction_returns_numeric_price():
    payload = {
        "Trip_Distance_km": 10.5,
        "Passenger_Count": 1,
        "Base_Fare": 50.0,
        "Per_Km_Rate": 18.0,
        "Per_Minute_Rate": 7.0,
        "Trip_Duration_Minutes": 15.0,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    price = response.json()["predicted_price"]
    assert isinstance(price, (int, float))
    assert price >= 0


def test_prediction_rejects_missing_features():
    response = client.post("/predict", json={"Trip_Distance_km": 10.5})
    assert response.status_code == 422
