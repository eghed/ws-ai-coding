import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np
from typing import Optional, Tuple, Dict, Any, List

def get_location() -> Tuple[Optional[float], Optional[float], Optional[str], Optional[str]]:
    """
    Get the user's geographical location using the IP-API service.
    
    Returns:
        Tuple[Optional[float], Optional[float], Optional[str], Optional[str]]: 
            A tuple containing latitude, longitude, city, and country
    """
    try:
        response = requests.get('http://ip-api.com/json/')
        if response.status_code == 200:
            location_data = response.json()
            return (
                location_data.get('lat'), 
                location_data.get('lon'),
                location_data.get('city'),
                location_data.get('country')
            )
        return None, None, None, None
    except Exception:
        return None, None, None, None

def search_location(query: str) -> List[Dict[str, Any]]:
    """
    Search for a location by name using the Nominatim API.
    
    Args:
        query: The location name to search for
        
    Returns:
        List[Dict[str, Any]]: List of matching locations
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query,
            "format": "json",
            "limit": 5,
            "addressdetails": 1
        }
        headers = {
            "User-Agent": "WeatherApp/1.0"  # Required by Nominatim's terms of use
        }
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.sidebar.error(f"Error searching for location: {e}")
        return []

def get_weather_data(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Fetch weather data from Open-Meteo API for the given coordinates.
    
    Args:
        latitude: The latitude coordinate
        longitude: The longitude coordinate
        
    Returns:
        Dict[str, Any]: Weather data response from the API
    """
    url = (f"https://api.open-meteo.com/v1/forecast"
           f"?latitude={latitude}&longitude={longitude}"
           f"&current_weather=true"
           f"&hourly=temperature_2m,relativehumidity_2m,precipitation_probability,cloudcover,windspeed_10m"
           f"&daily=weathercode,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum,precipitation_hours,windspeed_10m_max")
    
    response = requests.get(url)
    data = response.json()
    return data

def weather_code_to_description(code: int) -> str:
    """
    Convert weather code to human-readable description.
    
    Args:
        code: The weather code from the API
        
    Returns:
        str: Human-readable weather description
    """
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return weather_codes.get(code, f"Unknown ({code})")

def format_date(date_str: str) -> str:
    """
    Format date string to a more readable format.
    
    Args:
        date_str: Date string in ISO format
        
    Returns:
        str: Formatted date string
    """
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%a, %b %d")

def display_weather_data(data: Dict[str, Any], location_name: str = "") -> None:
    """
    Display weather data in the Streamlit app.
    
    Args:
        data: Weather data from the API
        location_name: Name of the location for display purposes
    """
    if "current_weather" in data:
        # Display location name if provided
        if location_name:
            st.header(f"Weather Forecast for {location_name}")
        
        # Display current weather
        st.subheader("Current Weather")
        weather = data["current_weather"]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Temperature", f"{weather['temperature']}°C")
        with col2:
            st.metric("Wind Speed", f"{weather['windspeed']} km/h")
        with col3:
            weather_desc = weather_code_to_description(weather['weathercode'])
            st.metric("Condition", weather_desc)
        
        # Display 7-day forecast
        if "daily" in data:
            st.subheader("7-Day Forecast")
            
            daily = data["daily"]
            dates = daily["time"]
            max_temps = daily["temperature_2m_max"]
            min_temps = daily["temperature_2m_min"]
            weather_codes = daily["weathercode"]
            wind_speeds = daily["windspeed_10m_max"]
            precip_sum = daily["precipitation_sum"]
            
            # Create a dataframe for the daily forecast
            daily_data = []
            for i in range(len(dates)):
                daily_data.append({
                    "Date": format_date(dates[i]),
                    "Max Temp": f"{max_temps[i]}°C",
                    "Min Temp": f"{min_temps[i]}°C",
                    "Condition": weather_code_to_description(weather_codes[i]),
                    "Wind": f"{wind_speeds[i]} km/h",
                    "Precipitation": f"{precip_sum[i]} mm"
                })
            
            # Display daily forecast as a table
            st.dataframe(pd.DataFrame(daily_data), use_container_width=True)
            
            # Create temperature chart
            temp_fig = px.line(
                x=[format_date(d) for d in dates],
                y=[max_temps, min_temps],
                labels={"x": "Date", "y": "Temperature (°C)"},
                title="7-Day Temperature Forecast",
                markers=True
            )
            temp_fig.update_layout(legend_title_text="")
            temp_fig.data[0].name = "Max Temperature"
            temp_fig.data[1].name = "Min Temperature"
            st.plotly_chart(temp_fig, use_container_width=True)
        
        # Display hourly precipitation probability
        if "hourly" in data:
            st.subheader("Hourly Precipitation Probability")
            
            hourly = data["hourly"]
            hourly_times = hourly["time"]
            precip_prob = hourly["precipitation_probability"]
            cloud_cover = hourly["cloudcover"]
            
            # Create a dataframe for the hourly data
            hourly_df = pd.DataFrame({
                "Time": [datetime.fromisoformat(t) for t in hourly_times],
                "Precipitation Probability": precip_prob,
                "Cloud Cover": cloud_cover
            })
            
            # Create precipitation probability chart
            precip_fig = px.bar(
                hourly_df,
                x="Time",
                y="Precipitation Probability",
                title="Hourly Precipitation Probability (%)",
                color_discrete_sequence=["#1E88E5"]
            )
            precip_fig.update_layout(
                xaxis_title="Date & Time",
                yaxis_title="Probability (%)",
                yaxis_range=[0, 100]
            )
            st.plotly_chart(precip_fig, use_container_width=True)
            
            # Create cloud cover chart
            cloud_fig = px.line(
                hourly_df,
                x="Time",
                y="Cloud Cover",
                title="Hourly Cloud Cover (%)",
                color_discrete_sequence=["#7E57C2"]
            )
            cloud_fig.update_layout(
                xaxis_title="Date & Time",
                yaxis_title="Cloud Cover (%)",
                yaxis_range=[0, 100]
            )
            st.plotly_chart(cloud_fig, use_container_width=True)
    else:
        st.error("Weather data not available for the provided coordinates.")

def main() -> None:
    """Main function to run the Streamlit weather application."""
    # Initialize session state for preserving data between reruns
    if 'locations' not in st.session_state:
        st.session_state.locations = []
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'selected_location_index' not in st.session_state:
        st.session_state.selected_location_index = 0
    if 'weather_data' not in st.session_state:
        st.session_state.weather_data = None
    if 'location_name' not in st.session_state:
        st.session_state.location_name = ""
    if 'current_lat' not in st.session_state:
        st.session_state.current_lat = None
    if 'current_lon' not in st.session_state:
        st.session_state.current_lon = None
    if 'first_load' not in st.session_state:
        st.session_state.first_load = True
    
    # Main title
    st.title("Weather Forecast")
    
    # Sidebar for all controls
    st.sidebar.title("Location Settings")
    
    # Get user's location on first load
    if st.session_state.first_load:
        auto_lat, auto_lon, auto_city, auto_country = get_location()
        if auto_lat and auto_lon and auto_city and auto_country:
            st.session_state.current_lat = auto_lat
            st.session_state.current_lon = auto_lon
            st.session_state.location_name = f"{auto_city}, {auto_country}"
            
            # Fetch weather data for detected location
            with st.spinner(f"Fetching weather data for {st.session_state.location_name}..."):
                st.session_state.weather_data = get_weather_data(auto_lat, auto_lon)
        
        st.session_state.first_load = False
    
    # Display current location information in sidebar
    if st.session_state.current_lat and st.session_state.current_lon:
        st.sidebar.success(f"Current location: {st.session_state.location_name}")
        st.sidebar.info(f"Coordinates: Lat {st.session_state.current_lat:.6f}, Lon {st.session_state.current_lon:.6f}")
    
    # Location selection method
    location_method = st.sidebar.radio(
        "Choose location method:",
        ["Current Location", "Search by City", "Enter Coordinates"]
    )
    
    # Handle different location selection methods
    if location_method == "Current Location":
        auto_lat, auto_lon, auto_city, auto_country = get_location()
        if auto_lat and auto_lon and auto_city and auto_country:
            st.sidebar.success(f"Detected: {auto_city}, {auto_country}")
            if st.sidebar.button("Use This Location"):
                st.session_state.current_lat = auto_lat
                st.session_state.current_lon = auto_lon
                st.session_state.location_name = f"{auto_city}, {auto_country}"
                
                with st.spinner(f"Fetching weather data for {st.session_state.location_name}..."):
                    st.session_state.weather_data = get_weather_data(auto_lat, auto_lon)
        else:
            st.sidebar.warning("Could not detect your location automatically.")
            st.sidebar.info("Please use another method to select a location.")
    
    elif location_method == "Search by City":
        st.sidebar.subheader("Search by City Name")
        search_query = st.sidebar.text_input(
            "Enter city name (e.g., 'New York', 'London, UK')", 
            value=st.session_state.search_query
        )
        
        if st.sidebar.button("Search"):
            if search_query:
                st.session_state.locations = search_location(search_query)
                st.session_state.search_query = search_query
                
                if st.session_state.locations:
                    st.sidebar.success(f"Found {len(st.session_state.locations)} locations")
                else:
                    st.sidebar.error(f"No locations found matching '{search_query}'")
        
        # Display search results if available
        if st.session_state.locations:
            location_options = []
            for loc in st.session_state.locations:
                display_name = loc.get("display_name", "Unknown location")
                location_options.append(display_name)
            
            selected_location = st.sidebar.selectbox(
                "Select a location:", 
                location_options,
                index=st.session_state.selected_location_index
            )
            
            if selected_location:
                st.session_state.selected_location_index = location_options.index(selected_location)
                selected_loc = st.session_state.locations[st.session_state.selected_location_index]
                selected_lat = float(selected_loc["lat"])
                selected_lon = float(selected_loc["lon"])
                
                if st.sidebar.button("Use Selected Location"):
                    st.session_state.current_lat = selected_lat
                    st.session_state.current_lon = selected_lon
                    st.session_state.location_name = selected_location
                    
                    with st.spinner(f"Fetching weather data for {selected_location}..."):
                        st.session_state.weather_data = get_weather_data(selected_lat, selected_lon)
    
    elif location_method == "Enter Coordinates":
        st.sidebar.subheader("Enter Exact Coordinates")
        
        default_lat = st.session_state.current_lat if st.session_state.current_lat else 0.0
        default_lon = st.session_state.current_lon if st.session_state.current_lon else 0.0
        
        latitude = st.sidebar.number_input("Latitude:", value=default_lat, format="%.6f")
        longitude = st.sidebar.number_input("Longitude:", value=default_lon, format="%.6f")
        location_name = st.sidebar.text_input("Location Name (optional):", 
                                             value="" if location_method != "Current Location" else st.session_state.location_name)
        
        if st.sidebar.button("Use These Coordinates"):
            if latitude != 0.0 or longitude != 0.0:  # Basic validation
                st.session_state.current_lat = latitude
                st.session_state.current_lon = longitude
                st.session_state.location_name = location_name if location_name else f"Lat: {latitude}, Lon: {longitude}"
                
                with st.spinner(f"Fetching weather data..."):
                    st.session_state.weather_data = get_weather_data(latitude, longitude)
            else:
                st.sidebar.error("Please enter valid coordinates.")
    
    # Display weather data in the main area if available
    if st.session_state.weather_data:
        display_weather_data(st.session_state.weather_data, st.session_state.location_name)
    elif not st.session_state.first_load:  # Don't show this message on first load
        st.info("Select a location to view weather forecast.")

if __name__ == "__main__":
    main()
