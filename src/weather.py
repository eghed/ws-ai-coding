import streamlit as st
import requests

def get_location() -> tuple[float, float]:
    """
    Get the user's geographical location using the IP-API service.
    
    Returns:
        tuple[float, float]: A tuple containing latitude and longitude
    """
    try:
        response = requests.get('http://ip-api.com/json/')
        if response.status_code == 200:
            location_data = response.json()
            return location_data.get('lat'), location_data.get('lon')
        return None, None
    except Exception:
        return None, None

def get_weather_data(latitude: float, longitude: float) -> dict:
    """
    Fetch weather data from Open-Meteo API for the given coordinates.
    
    Args:
        latitude: The latitude coordinate
        longitude: The longitude coordinate
        
    Returns:
        dict: Weather data response from the API
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    response = requests.get(url)
    data = response.json()
    return data

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
            data = get_weather_data(latitude, longitude)
            if "current_weather" in data:
                weather = data["current_weather"]
                st.write(f"**Temperature:** {weather['temperature']}°C")
                st.write(f"**Wind Speed:** {weather['windspeed']} km/h")
                st.write(f"**Weather Code:** {weather['weathercode']}")
            else:
                st.error("Weather data not available for the provided coordinates.")
        else:
            st.error("Please enter valid latitude and longitude.")

if __name__ == "__main__":
    main()
