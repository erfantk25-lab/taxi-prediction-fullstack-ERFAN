# Taxi Fare Prediction — Full-Stack ML Application

A full-stack machine-learning application that estimates taxi fares from trip information. The project separates the user interface from the prediction API and connects route information to a model prediction.

## Project overview

- **Frontend:** Streamlit interface.
- **Backend:** FastAPI service exposing prediction and data-inspection endpoints.
- **Route data:** OpenRouteService is used to retrieve route information.
- **Map visualization:** Folium displays the returned route.
- **Prediction:** The backend returns an estimated fare from the supplied trip data.

## Request flow

1. The user enters trip details in the Streamlit application.
2. The application requests route information from OpenRouteService.
3. The route distance and estimated duration are included in the request to the FastAPI backend.
4. The backend calls the machine-learning model and returns a fare estimate.
5. The frontend displays the estimate and route visualization.

## Backend API

FastAPI provides interactive API documentation at `/docs` when the backend is running.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/predict` | Return a fare prediction. |
| `GET` | `/data/head` | Retrieve a sample of the training data. |
| `GET` | `/data/trip/{trip_id}` | Retrieve a trip by its ID. |

## Screenshots

The repository includes screenshots illustrating the API documentation, main application, and endpoint tests:

- `screenshots/Image 1.png` — backend API documentation.
- `screenshots/Image 2.png` — main application view.
- `screenshots/Image 3.png` and `screenshots/Image 4.png` — application/backend startup.
- `screenshots/Image 5.png` — data endpoint test.
- `screenshots/Image 6.png` — prediction endpoint test.

## Technologies

Python · Streamlit · FastAPI · OpenRouteService · Folium · Machine Learning

## Notes

The frontend and backend run as separate processes. The OpenRouteService integration requires a valid API configuration. Check the project source and configuration files for the exact local startup commands and required environment variables.

---

This is a learning project demonstrating an end-to-end application flow from route retrieval to model-backed prediction.
