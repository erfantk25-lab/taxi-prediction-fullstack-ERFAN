import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import openrouteservice

# AI-assisted code: Added session state management to retain results and map between script reruns.
st.set_page_config(layout="wide")
st.title("Taxi Price Prediction 2.0")
st.markdown("Fill in the start and end address below to get a predicted taxi price and see the route on a map.")

# AI-assisted code: This block was added to solve the "disappearing results" issue, which is a common challenge in Streamlit. 
if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None
if 'folium_map' not in st.session_state:
    st.session_state.folium_map = None

# AI-assisted code: This block handles the connection to the external API using the secret key, including the error handling.
try:
    ors_client = openrouteservice.Client(key=st.secrets['ORS_API_KEY'])
except Exception:
    st.error("Could not connect to Openrouteservice. Please check your API key in .streamlit/secrets.toml.")
    ors_client = None

API_URL = "http://127.0.0.1:8000/predict"

col1, col2 = st.columns([1, 2]) 

with col1:
    st.subheader("Trip Information")

    start_address = st.text_input("Start Address (Location A)", "Stockholm Central Station")
    end_address = st.text_input("End Address (Location B)", "Avicii Arena, Stockholm")
    
    
    passenger_count = st.number_input("Number of Passengers", min_value=1, max_value=8, value=1)
    base_fare = st.number_input("Base Fare (SEK)", min_value=0.0, value=50.0, step=1.0, format="%.2f")
    per_km_rate = st.number_input("Price per km (SEK)", min_value=0.0, value=18.0, step=0.1, format="%.2f")
    per_minute_rate = st.number_input("Price per minute (SEK)", min_value=0.0, value=7.0, step=0.1, format="%.2f")

    predict_button = st.button("Calculate Price and Show Route")


if predict_button and ors_client:
    if not start_address or not end_address:
        st.warning("Please fill in both start and end address.")
    else:
        try:
            # AI-assisted bug fix: The original attempt to find both addresses in one API call failed.
            start_geocode = ors_client.pelias_search(text=start_address, size=1)
            if not start_geocode['features']:
                raise ValueError(f"Could not find coordinates for start address: '{start_address}'")
            start_coords = start_geocode['features'][0]['geometry']['coordinates']

            end_geocode = ors_client.pelias_search(text=end_address, size=1)
            if not end_geocode['features']:
                raise ValueError(f"Could not find coordinates for end address: '{end_address}'")
            end_coords = end_geocode['features'][0]['geometry']['coordinates']

            coords_list = [start_coords, end_coords]
            route = ors_client.directions(coordinates=coords_list, profile='driving-car', format='geojson')
            
            summary = route['features'][0]['properties']['summary']
            distance_km = summary['distance'] / 1000  
            duration_min = summary['duration'] / 60    
            
            payload = {
                "Trip_Distance_km": distance_km,
                "Passenger_Count": passenger_count,
                "Base_Fare": base_fare,
                "Per_Km_Rate": per_km_rate,
                "Per_Minute_Rate": per_minute_rate,
                "Trip_Duration_Minutes": duration_min
            }
            response = requests.post(API_URL, json=payload)
            response.raise_for_status() 
            prediction = response.json()
            predicted_price = prediction.get('predicted_price')
            
            # AI-assisted code: Creating the folium map with the route
            route_geometry = route['features'][0]['geometry']['coordinates']
            swapped_route = [(coord[1], coord[0]) for coord in route_geometry]
            m = folium.Map(location=swapped_route[0], zoom_start=13)
            folium.PolyLine(swapped_route, color="blue", weight=5, opacity=0.8).add_to(m)
            folium.Marker(swapped_route[0], popup="Start", tooltip=start_address).add_to(m)
            folium.Marker(swapped_route[-1], popup="End", tooltip=end_address).add_to(m)
            
            # AI-assisted bug fix: Instead of displaying results directly, they are saved to the session state to make them persistent.
            st.session_state.prediction_result = {
                "distance": distance_km,
                "duration": duration_min,
                "price": predicted_price
            }
            st.session_state.folium_map = m

        except Exception as e:
            st.session_state.prediction_result = {'error': f"An error occurred. Please check that the addresses are correct. Error: {e}"}
            st.session_state.folium_map = None

# AI-assisted code: Idead to display results and map from session state.
with col2:
    st.subheader("Map and Price")
    
    if st.session_state.folium_map:
        st_folium(st.session_state.folium_map, width=700, height=450)
    else:
        m_initial = folium.Map(location=[59.33, 18.06], zoom_start=11)
        st_folium(m_initial, width=700, height=450)
    
    if st.session_state.prediction_result:
        if 'error' in st.session_state.prediction_result:
            st.error(st.session_state.prediction_result['error'])
        else:
            res = st.session_state.prediction_result
            st.success(f"Calculated distance: {res['distance']:.2f} km\n\n"
                         f"Calculated travel time: {res['duration']:.2f} minutes\n\n"
                         f"### Predicted Price: {res['price']:.2f} SEK")


