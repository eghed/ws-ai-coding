import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np
from typing import Optional, Tuple, Dict, Any

def get_location() -> Tuple[Optional[float], Optional[float]]:
    """
    Get the user's geographical location using the IP-API service.
    
    Returns:
        Tuple[Optional[float], Optional[float]]: A tuple containing latitude and longitude
    """
    try:
        response = requests.get('http://ip-api.com/json/')
        if response.status_code == 200:
            location_data = response.json()
            return location_data.get('lat'), location_data.get('lon')
        return None, None
    except Exception:
        return None, None

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

def main() -> None:
    """Main function to run the Streamlit weather application."""
    st.title("Weather App using Open-Meteo API")
    
    # Get user's location
    auto_lat, auto_lon = get_location()
    
    # Use detected location or allow manual input
    use_current_location = st.checkbox("Use my current location", value=True if auto_lat and auto_lon else False)
    
    if use_current_location and auto_lat and auto_lon:
        st.info(f"Using detected location: Lat {auto_lat:.6f}, Lon {auto_lon:.6f}")
        latitude = auto_lat
        longitude = auto_lon
    else:
        # Input fields for latitude and longitude
        latitude = st.number_input("Enter Latitude:", value=auto_lat if auto_lat else 0.0, format="%.6f")
        longitude = st.number_input("Enter Longitude:", value=auto_lon if auto_lon else 0.0, format="%.6f")
    
    if st.button("Get Weather"):
        if latitude and longitude:
            with st.spinner("Fetching weather data..."):
                data = get_weather_data(latitude, longitude)
                
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
        else:
            st.error("Please enter valid latitude and longitude.")

if __name__ == "__main__":
    main()
