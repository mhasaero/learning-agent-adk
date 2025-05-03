import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
import datetime
from zoneinfo import ZoneInfo
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import requests


def get_weather(city: str) -> dict:
    """
    Retrieves the current weather report for a specified city using Open-Meteo API.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error message.
    """
    try:
        # Geocode the city to get latitude and longitude
        geolocator = Nominatim(user_agent="weather_app")
        location = geolocator.geocode(city)
        if not location:
            return {
                "status": "error",
                "error_message": f"Could not find the city: {city}."
            }

        latitude = location.latitude
        longitude = location.longitude

        # Call Open-Meteo API for current weather
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "current_weather" not in data:
            return {
                "status": "error",
                "error_message": f"Weather data not available for {city}."
            }

        weather = data["current_weather"]
        temperature_c = weather["temperature"]
        wind_speed = weather["windspeed"]
        weather_code = weather["weathercode"]

        report = (
            f"The current temperature in {city} is {temperature_c:.1f}°C "
            f"with a wind speed of {wind_speed} km/h. "
            f"Weather code: {weather_code}."
        )

        return {"status": "success", "report": report}

    except requests.exceptions.RequestException as req_err:
        return {
            "status": "error",
            "error_message": f"Request error: {req_err}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"An unexpected error occurred: {e}"
        }


def get_current_time(city: str) -> dict:
    """
    Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error message.
    """
    try:
        # Initialize geolocator and timezone finder
        geolocator = Nominatim(user_agent="city_time_app")
        tf = TimezoneFinder()

        # Geocode the city to get latitude and longitude
        location = geolocator.geocode(city)
        if not location:
            return {
                "status": "error",
                "error_message": f"Could not find the city: {city}."
            }

        # Find the timezone name using latitude and longitude
        timezone_name = tf.timezone_at(lng=location.longitude, lat=location.latitude)
        if not timezone_name:
            return {
                "status": "error",
                "error_message": f"Could not determine the timezone for {city}."
            }

        # Get the current time in the found timezone
        tz = ZoneInfo(timezone_name)
        now = datetime.datetime.now(tz)
        report = f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
        return {"status": "success", "report": report}

    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    tools=[get_weather, get_current_time],
)