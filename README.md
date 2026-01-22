# taxi-prediction-fullstack-ERFAN





# Backend API Documentation

The project's backend is a standalone API built with FastAPI. A major advantage of using FastAPI is that it automatically generates interactive API documentation from the code, as shown in this screenshot (accessible at the /docs endpoint).

This serves as a clear "contract" for how the frontend—or any other client—should communicate with the backend. It clearly lists all available endpoints, such as:

POST /predict: For getting a price prediction.

GET /data/head: For retrieving sample training data.

GET /data/trip/{trip_id}: For fetching a specific trip by its ID.

This proves that the application follows the required architecture, with a well-defined and independent backend service that is completely separate from the frontend.

## See: screenshots/Image 1.png



## Main Application View

This is the primary user interface of the Taxi Price Prediction application, built with Streamlit. The screenshot below shows a complete, successful user interaction. The application has:
Fetched Route Data: It sends the addresses to the external Openrouteservice API. The returned route is then visualized as a blue line on the interactive Folium map.
Extracted Trip Details: Key information like the total distance (9.50 km) and estimated travel time (13.18 minutes) is extracted from the API response and displayed to the user.
Called the Backend API: This new data is sent to our own FastAPI backend's /predict endpoint.
Displayed the Final Price: The price predicted by the machine learning model is returned from the backend and shown in the green result box (28.17 SEK).
This single view demonstrates the successful end-to-end integration of the frontend, backend, and the external mapping service.
## See: screenshots/Image 2.png


## Running the Application (System Architecture)

The project is built on a fullstack architecture with a separate backend and frontend, which must be run as two independent processes in separate terminals.
1. Backend Server (Left Image): The first terminal runs the FastAPI backend using uvicorn. The logs confirm that the server has started successfully, the machine learning model has been loaded (INFO: Model file loaded successfully), and it is ready to accept requests.
2. Frontend Server (Right Image): The second terminal runs the Streamlit frontend using streamlit run. The output provides the local URL (http://localhost:8501) where the user can access and interact with the web application in their browser.
This setup demonstrates the decoupled nature of the application, which is a core concept in modern MLOps and web development.

## See: screenshots/Image 3.png and screenshots/Image 4.png



## Testing the Data Endpoints

Beyond its prediction capabilities, the API also includes utility endpoints for inspecting the training data. This screenshot shows the /data/head endpoint being tested.
A parameter n is set to 120 to request the first 120 rows of the dataset.
The "Execute" button is clicked, sending a GET request to the server.
The server successfully responds with a 200 OK status and a JSON array containing the requested trip data.
This functionality is useful for debugging, verification, or for any client application that might need to display sample data.
## See: screenshots/Image 5.png



## Testing the /predict Endpoint

The interactive documentation allows for direct testing of each endpoint, independent of the frontend. This screenshot shows the /predict endpoint being tested using the "Try it out" feature.
A JSON object with sample trip data is provided as the Request body.
The "Execute" button is clicked, sending a POST request to the server.
The server successfully responds with a 200 OK status code and a JSON object containing the predicted_price (28.19 in this case).
This confirms that the backend logic and the machine learning model are working correctly and can be tested and verified on their own.

## See: screenshots/Image 6.png