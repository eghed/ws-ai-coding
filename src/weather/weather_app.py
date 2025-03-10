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
        st.error(f"Error searching for location: {e}")
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

def display_weather_data(data: Dict[str, Any]) -> None:
    """
    Display weather data in the Streamlit app.
    
    Args:
        data: Weather data from the API
    """
    if "current_weather" in data:
        # Display current weather
        st.header("Current Weather")
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
            st.header("7-Day Forecast")
            
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
            st.header("Hourly Precipitation Probability")
            
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
    # Initialize session state for preserving search results
    if 'search_performed' not in st.session_state:
        st.session_state.search_performed = False
    if 'locations' not in st.session_state:
        st.session_state.locations = []
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'selected_location_index' not in st.session_state:
        st.session_state.selected_location_index = 0
    if 'weather_data' not in st.session_state:
        st.session_state.weather_data = None
    
    st.title("Weather App using Open-Meteo API")
    
    # Get user's location
    auto_lat, auto_lon, auto_city, auto_country = get_location()
    
    # Create tabs for different input methods
    location_tab, search_tab = st.tabs(["Current Location", "Search by City"])
    
    with location_tab:
        # Use detected location or allow manual input
        if auto_lat and auto_lon and auto_city and auto_country:
            location_info = f"{auto_city}, {auto_country}"
            st.success(f"Detected location: {location_info}")
            use_current_location = st.checkbox("Use my current location", value=True)
            
            if use_current_location:
                st.info(f"Using coordinates: Lat {auto_lat:.6f}, Lon {auto_lon:.6f}")
                latitude = auto_lat
                longitude = auto_lon
                
                if st.button("Get Weather for Current Location"):
                    with st.spinner(f"Fetching weather data for {location_info}..."):
                        data = get_weather_data(latitude, longitude)
                        display_weather_data(data)
            else:
                st.info("Enter coordinates manually below")
                latitude = st.number_input("Enter Latitude:", value=auto_lat, format="%.6f")
                longitude = st.number_input("Enter Longitude:", value=auto_lon, format="%.6f")
                
                if st.button("Get Weather for Coordinates"):
                    with st.spinner("Fetching weather data..."):
                        data = get_weather_data(latitude, longitude)
                        display_weather_data(data)
        else:
            st.warning("Could not detect your location automatically.")
            st.info("Enter coordinates manually below")
            latitude = st.number_input("Enter Latitude:", value=0.0, format="%.6f")
            longitude = st.number_input("Enter Longitude:", value=0.0, format="%.6f")
            
            if st.button("Get Weather for Coordinates"):
                if latitude != 0.0 or longitude != 0.0:  # Basic validation
                    with st.spinner("Fetching weather data..."):
                        data = get_weather_data(latitude, longitude)
                        display_weather_data(data)
                else:
                    st.error("Please enter valid latitude and longitude.")
    
    with search_tab:
        st.subheader("Search by City Name")
        
        # Search input and button
        search_query = st.text_input("Enter city name (e.g., 'New York', 'London, UK')", 
                                     value=st.session_state.search_query)
        
        search_col1, search_col2 = st.columns([1, 3])
        with search_col1:
            search_clicked = st.button("Search Location")
        
        # If search button is clicked, perform the search
        if search_clicked and search_query:
            with st.spinner(f"Searching for '{search_query}'..."):
                st.session_state.locations = search_location(search_query)
                st.session_state.search_performed = True
                st.session_state.search_query = search_query
                st.session_state.weather_data = None  # Reset weather data
        
        # If search has been performed, show results
        if st.session_state.search_performed and st.session_state.locations:
            st.success(f"Found {len(st.session_state.locations)} locations matching '{st.session_state.search_query}'")
            
            # Create a list of location options for the user to select
            location_options = []
            for loc in st.session_state.locations:
                display_name = loc.get("display_name", "Unknown location")
                lat = float(loc.get("lat", 0))
                lon = float(loc.get("lon", 0))
                location_options.append(f"{display_name} (Lat: {lat:.4f}, Lon: {lon:.4f})")
            
            # Display the dropdown with the location options
            selected_location = st.selectbox(
                "Select a location:", 
                location_options,
                index=st.session_state.selected_location_index
            )
            
            # Update the selected location index in session state
            if selected_location:
                st.session_state.selected_location_index = location_options.index(selected_location)
            
            # Get weather button
            get_weather_clicked = st.button("Get Weather for Selected Location")
            
            # If get weather button is clicked or weather data already exists, display it
            if get_weather_clicked:
                selected_index = st.session_state.selected_location_index
                selected_lat = float(st.session_state.locations[selected_index]["lat"])
                selected_lon = float(st.session_state.locations[selected_index]["lon"])
                location_name = selected_location.split(' (Lat')[0]
                
                with st.spinner(f"Fetching weather data for {location_name}..."):
                    st.session_state.weather_data = get_weather_data(selected_lat, selected_lon)
            
            # Display weather data if it exists
            if st.session_state.weather_data:
                display_weather_data(st.session_state.weather_data)
                
        elif st.session_state.search_performed:
            st.error(f"No locations found matching '{st.session_state.search_query}'. Try a different search term.")

if __name__ == "__main__":
    main()
