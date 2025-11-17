import requests
import random
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class FreeWeatherAPIs:
    """Free Weather API integrations"""
    
    @staticmethod
    def get_weatherapi(lat: float, lon: float, api_key: str) -> Optional[Dict]:
        """Get weather from WeatherAPI.com"""
        try:
            url = f"http://api.weatherapi.com/v1/current.json"
            params = {
                "key": api_key,
                "q": f"{lat},{lon}",
                "aqi": "no"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            location = data.get("location", {})
            
            return {
                "temperature_celsius": current.get("temp_c", 0),
                "temperature_fahrenheit": current.get("temp_f", 0),
                "feels_like_celsius": current.get("feelslike_c", 0),
                "condition": current.get("condition", {}).get("text", "Unknown"),
                "description": f"Currently {current.get('condition', {}).get('text', 'unknown').lower()}",
                "humidity_percent": current.get("humidity", 0),
                "wind_speed_kmh": current.get("wind_kph", 0),
                "wind_direction": current.get("wind_dir", "NA"),
                "pressure_mb": current.get("pressure_mb", 1013),
                "visibility_km": current.get("vis_km", 10),
                "uv_index": current.get("uv", 0),
                "cloud_cover_percent": current.get("cloud", 0),
                "precipitation_mm": current.get("precip_mm", 0),
                "is_real_data": True,
                "source": "WeatherAPI.com"
            }
        except Exception as e:
            logger.debug(f"WeatherAPI failed: {e}")
            return None
    
    @staticmethod
    def get_open_meteo(lat: float, lon: float) -> Optional[Dict]:
        """Get weather from Open-Meteo API"""
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,pressure_msl,cloud_cover,wind_speed_10m",
                "timezone": "auto"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            weather_codes = {
                0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy",
                3: "Overcast", 45: "Foggy", 61: "Slight rain",
                63: "Moderate rain", 65: "Heavy rain", 71: "Slight snow",
                73: "Moderate snow", 95: "Thunderstorm"
            }
            
            condition = weather_codes.get(current.get("weather_code", 0), "Unknown")
            temp_c = current.get("temperature_2m", 0)
            
            return {
                "temperature_celsius": temp_c,
                "temperature_fahrenheit": round((temp_c * 9/5) + 32, 1),
                "feels_like_celsius": current.get("apparent_temperature", temp_c),
                "condition": condition,
                "description": f"Currently {condition.lower()}",
                "humidity_percent": current.get("relative_humidity_2m", 50),
                "wind_speed_kmh": current.get("wind_speed_10m", 0),
                "wind_direction": "NA",
                "pressure_mb": current.get("pressure_msl", 1013),
                "visibility_km": 10,
                "uv_index": 0,
                "cloud_cover_percent": current.get("cloud_cover", 0),
                "precipitation_mm": current.get("precipitation", 0),
                "is_real_data": True,
                "source": "Open-Meteo"
            }
        except Exception as e:
            logger.debug(f"Open-Meteo failed: {e}")
            return None
    
    @staticmethod
    def get_mock_weather(lat: float, lon: float) -> Dict:
        """Generate mock weather data"""
        base_temp = 25 - (abs(lat) * 0.5)
        temp_c = round(base_temp + random.uniform(-5, 8), 1)
        conditions = ["Clear sky", "Partly cloudy", "Cloudy", "Light rain"]
        condition = random.choice(conditions)
        
        return {
            "temperature_celsius": temp_c,
            "temperature_fahrenheit": round((temp_c * 9/5) + 32, 1),
            "feels_like_celsius": round(temp_c + random.uniform(-2, 2), 1),
            "condition": condition,
            "description": f"Currently {condition.lower()}",
            "humidity_percent": random.randint(40, 85),
            "wind_speed_kmh": round(random.uniform(5, 25), 1),
            "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
            "pressure_mb": random.randint(1005, 1025),
            "visibility_km": random.randint(8, 20),
            "uv_index": random.randint(1, 9),
            "cloud_cover_percent": random.randint(10, 90),
            "precipitation_mm": 0,
            "is_mock_data": True,
            "is_real_data": False,
            "source": "Mock Data"
        }
    
    @staticmethod
    def get_weather(lat: float, lon: float, api_key: str = None) -> Dict:
        """Get weather from available sources with fallback"""
        logger.info(f"Fetching weather for {lat:.4f}, {lon:.4f}")
        
        if api_key:
            weather_data = FreeWeatherAPIs.get_weatherapi(lat, lon, api_key)
            if weather_data:
                logger.info("Using WeatherAPI.com")
                return weather_data
        
        weather_data = FreeWeatherAPIs.get_open_meteo(lat, lon)
        if weather_data:
            logger.info("Using Open-Meteo")
            return weather_data
        
        logger.warning("Using mock data")
        return FreeWeatherAPIs.get_mock_weather(lat, lon)
