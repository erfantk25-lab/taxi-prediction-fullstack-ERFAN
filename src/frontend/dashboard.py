import streamlit as st
import requests

st.title("Taxi Price Prediction")

st.write("Fyll i informationen nedan för att få ett förutsagt taxipris.")


distance = st.number_input("Trip Distance (km)", min_value=0.0, step=0.1)
passengers = st.number_input("Passenger Count", min_value=1, step=1)
base_fare = st.number_input("Base Fare", min_value=0.0, step=0.1)
per_km_rate = st.number_input("Per Km Rate", min_value=0.0, step=0.1)
per_minute_rate = st.number_input("Per Minute Rate", min_value=0.0, step=0.1)
duration = st.number_input("Trip Duration (minutes)", min_value=0.0, step=1.0)

if st.button("Predict Price"):
    payload = {
        "Trip_Distance_km": distance,
        "Passenger_Count": passengers,
        "Base_Fare": base_fare,
        "Per_Km_Rate": per_km_rate,
        "Per_Minute_Rate": per_minute_rate,
        "Trip_Duration_Minutes": duration
    }

    response = requests.post("http://127.0.0.1:8000/predict", json=payload)

    if response.status_code == 200:
        result = response.json()
        st.success(f"Predicted Price: {result['predicted_price']} SEK")
    else:
        st.error("Error: Could not get prediction from API.")