import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# Set page title
st.set_page_config(page_title="🚲 Bike Demand Predictor", layout="centered")


# ---- Add Custom CSS for Background Styling ----
page_bg = """
<style>
/* Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #1c2833, #283747, #34495e); /* Darker, gradient background */
    color: #ecf0f1; /* Light text for contrast */
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #17202a; /* Darker sidebar */
    color: #ecf0f1;
}

/* Text Styling */
h1, h2, h3, h4, h5, h6 {
    color: #ecf0f1; /* Light text */
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Subtle text shadow */
}

p, label {
    color: #d0d3d4; /* Slightly less bright text */
    font-family: 'Arial', sans-serif;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(to right, #6a11cb, #2575fc); /* Gradient button */
    color: white;
    border-radius: 20px; /* More rounded buttons */
    padding: 12px 24px; /* Slightly larger padding */
    font-size: 16px;
    font-weight: 600; /* Semi-bold font */
    border: none; /* Remove default border */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Add shadow for depth */
    transition: transform 0.2s ease-in-out; /* Smooth transition on hover */
}

.stButton>button:hover {
    transform: translateY(-2px); /* Slight lift on hover */
    box-shadow: 0 6px 10px rgba(0, 0, 0, 0.3); /* Enhanced shadow on hover */
}

/* Input boxes and other elements */
input, textarea, select {
    background-color: #2c3e50; /* Dark input background */
    color: #ecf0f1;
    border: 1px solid #34495e;
    border-radius: 8px;
    padding: 8px;
    font-size: 14px;
}

input:focus, textarea:focus, select:focus {
    border-color: #3498db; /* Highlight border on focus */
    outline: none; /* Remove default focus outline */
    box-shadow: 0 0 5px rgba(52, 152, 219, 0.5); /* Add focus shadow */
}

/* Add some spacing for better readability */
[data-testid="stVerticalBlock"] > div:first-child {
    padding-top: 20px;
}

</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# Function to fetch weather data
def get_weather_data(city):
    API_KEY = "6a9cd504a10b7fee9e0e137a61fde436"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200:
        temp = data["main"]["temp"] / 41  # Normalize (Max temp ~41°C)
        atemp = temp  # Assume atemp ≈ temp
        hum = data["main"]["humidity"] / 100  # Normalize (Max humidity 100%)
        windspeed = data["wind"]["speed"] / 67  # Normalize (Max windspeed ~67m/s)
        
        return temp, atemp, hum, windspeed
    else:
        return None, None, None, None

# Load trained model
import pickle
with open("bike_demand_model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

# Streamlit UI
st.image("Bike.PNG", use_column_width=True, width=20)
st.title("🚴‍♂️ Bike Demand Prediction App")
#st.title("Rent a Bike, Discover More")
st.subheader("🚲Rent a Bike, Discover More", divider=True)
st.logo("Bike.PNG",size= 'large')

# Sidebar Inputs
st.sidebar.header("🛠 User Inputs")

# Date Picker
selected_date = st.sidebar.date_input("📅 Select a Date")
month = selected_date.month
weekday = selected_date.weekday()
hour = st.sidebar.slider("⏰ Hour of the Day", 0, 23, 12)

# City Input for Weather Data
city = st.sidebar.text_input("🌍 Enter the Store Location", "New Delhi")

# Dropdowns for other categorical inputs
season = st.sidebar.selectbox("🌤 Season", [1, 2, 3, 4], format_func=lambda x: ["Spring", "Summer", "Fall", "Winter"][x-1])
holiday = st.sidebar.selectbox("🏖 Holiday", [0, 1], format_func=lambda x: 'No' if x==0 else 'Yes')
workingday = st.sidebar.selectbox("💼 Working Day", [0, 1], format_func=lambda x: 'No' if x==0 else "Yes")  # 0: No, 1: Yes
#weathersit = st.sidebar.selectbox("🌦 Weather Situation", [1, 2, 3, 4])  # 1: Clear, 2: Cloudy, 3: Light Rain, 4: Heavy Rain
weathersit = st.sidebar.selectbox("🌦 Weather Situation", [1, 2, 3, 4], format_func = lambda x: ['Clear','Cloudy','Light Rain','Heavy Rain'][x-1])

# Predict button
if st.sidebar.button("🚀 Predict Bike Demand"):
    temp, atemp, hum, windspeed = get_weather_data(city)

    if temp is not None:
        input_data = pd.DataFrame([[season, month, hour, holiday, weekday, workingday, weathersit, temp, atemp, hum, windspeed]], 
                                  columns=["season", "mnth", "hr", "holiday", "weekday", "workingday", "weathersit", "temp", "atemp", "hum", "windspeed"])

        predicted_bikes = model.predict(input_data)[0]
        
        st.success(f"🚲 **Predicted Bike Demand: {int(predicted_bikes)} bikes required.**")
    else:
        st.error("❌ Unable to fetch weather data. Please check the city name.")

