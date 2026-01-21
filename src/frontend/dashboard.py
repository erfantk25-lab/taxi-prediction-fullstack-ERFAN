import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import openrouteservice

# ====================================================================
# CONFIGURATION AND INITIALIZATION
# ====================================================================

st.set_page_config(layout="wide")
st.title("Taxi Price Prediction 2.0")
st.markdown("Fill in the start and end address below to get a predicted taxi price and see the route on a map.")

# Initialize the Openrouteservice client with your API key from secrets.toml
try:
    ors_client = openrouteservice.Client(key=st.secrets['ORS_API_KEY'])
except Exception:
    st.error("Could not connect to Openrouteservice. Please check your API key in .streamlit/secrets.toml.")
    ors_client = None

# URL to your own FastAPI backend
API_URL = "http://127.0.0.1:8000/predict"

# ====================================================================
# USER INPUT (Left column)
# ====================================================================

col1, col2 = st.columns([1, 2]) 

with col1:
    st.subheader("Trip Information")
    
    # Text input for addresses
    start_address = st.text_input("Start Address (Location A)", "Stockholm Central Station")
    end_address = st.text_input("End Address (Location B)", "Avicii Arena, Stockholm")
    
    # Other input fields
    passenger_count = st.number_input("Number of Passengers", min_value=1, max_value=8, value=1)
    base_fare = st.number_input("Base Fare (SEK)", min_value=0.0, value=50.0, step=1.0, format="%.2f")
    per_km_rate = st.number_input("Price per km (SEK)", min_value=0.0, value=18.0, step=0.1, format="%.2f")
    per_minute_rate = st.number_input("Price per minute (SEK)", min_value=0.0, value=7.0, step=0.1, format="%.2f")

    # The button that starts the calculation
    predict_button = st.button("Calculate Price and Show Route")

# ====================================================================
# MAP AND RESULTS (Right column)
# ====================================================================

with col2:
    st.subheader("Map and Price")
    map_placeholder = st.empty()
    result_placeholder = st.empty()

    # Display a default map of Stockholm before the user makes a selection
    m_initial = folium.Map(location=[59.33, 18.06], zoom_start=11)
    with map_placeholder:
        st_folium(m_initial, width=700, height=450)

# ====================================================================
# LOGIC: What happens when the button is pressed
# ====================================================================

if predict_button and ors_client:
    if not start_address or not end_address:
        st.warning("Please fill in both start and end address.")
    else:
        try:
            # 1. GET ROUTE FROM OPENROUTESERVICE
            # First: convert addresses to coordinates (lat, lon)
            locations = ors_client.pelias_search(text=f"{start_address} and {end_address}", size=2)
            coords = [loc['geometry']['coordinates'] for loc in locations['features']]
            
            # Then: Get the route information (distance, time, geometry) between the coordinates
            route = ors_client.directions(coordinates=coords, profile='driving-car', format='geojson')

            # 2. EXTRACT DISTANCE AND TIME
            summary = route['features'][0]['properties']['summary']
            distance_km = summary['distance'] / 1000  # From meters to km
            duration_min = summary['duration'] / 60    # From seconds to minutes
            
            # 3. CALL YOUR OWN PREDICTION API
            payload = {
                "Trip_Distance_km": distance_km,
                "Passenger_Count": passenger_count,
                "Base_Fare": base_fare,
                "Per_Km_Rate": per_km_rate,
                "Per_Minute_Rate": per_minute_rate,
                "Trip_Duration_Minutes": duration_min
            }
            response = requests.post(API_URL, json=payload)
            response.raise_for_status() # Throws an error if the call fails
            
            # 4. DISPLAY THE RESULT
            prediction = response.json()
            predicted_price = prediction.get('predicted_price')
            result_placeholder.success(f"Calculated distance: {distance_km:.2f} km\n\n"
                                     f"Calculated travel time: {duration_min:.2f} minutes\n\n"
                                     f"### Predicted Price: {predicted_price:.2f} SEK")
            
            # 5. DRAW THE MAP
            route_geometry = route['features'][0]['geometry']['coordinates']
            # Folium needs (lat, lon), ORS provides (lon, lat), so we need to swap them
            swapped_route = [(coord[1], coord[0]) for coord in route_geometry]

            m = folium.Map(location=swapped_route[0], zoom_start=13)
            folium.PolyLine(swapped_route, color="blue", weight=5, opacity=0.8).add_to(m)
            folium.Marker(swapped_route[0], popup="Start", tooltip=start_address).add_to(m)
            folium.Marker(swapped_route[-1], popup="End", tooltip=end_address).add_to(m)

            with map_placeholder:
                st_folium(m, width=700, height=450)

        except Exception as e:
            result_placeholder.error(f"An error occurred. Please check that the addresses are correct. Error: {e}")