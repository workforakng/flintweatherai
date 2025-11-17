import random
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class FreeAIAPIs:
    """Fallback AI chatbot responses"""
    
    @staticmethod
    def get_chat_response(message: str, weather_data: Dict) -> str:
        """Generate chatbot response based on message and weather"""
        message_lower = message.lower()
        current = weather_data.get("current_weather", {})
        location = weather_data.get("location", {})
        
        temp = current.get("temperature_celsius", 0)
        temp_f = current.get("temperature_fahrenheit", 0)
        condition = current.get("condition", "").lower()
        city = location.get("city", "your location")
        
        # Greetings
        if any(w in message_lower for w in ["hello", "hi", "hey"]):
            return f"👋 Hello! Weather in {city}: {condition}, {temp}°C. How can I help?"
        
        # Temperature queries
        if any(w in message_lower for w in ["temperature", "temp", "hot", "cold"]):
            feels = current.get("feels_like_celsius", temp)
            if temp > 35:
                advice = "🔥 Very hot! Stay hydrated and avoid sun."
            elif temp > 25:
                advice = "☀️ Warm! Good weather."
            elif temp > 15:
                advice = "😊 Pleasant temperature."
            elif temp > 5:
                advice = "🧥 Cool, wear a jacket."
            else:
                advice = "❄️ Cold! Bundle up."
            return f"Temperature: {temp}°C ({temp_f}°F), feels like {feels}°C. {advice}"
        
        # Rain queries
        if any(w in message_lower for w in ["rain", "umbrella", "wet"]):
            precip = current.get("precipitation_mm", 0)
            if "rain" in condition or precip > 0:
                return f"🌧️ Yes, {condition} with {precip}mm precipitation. Bring umbrella!"
            return f"☀️ No rain. It's {condition}."
        
        # Humidity queries
        if any(w in message_lower for w in ["humidity", "humid"]):
            humidity = current.get("humidity_percent", 0)
            if humidity > 80:
                return f"💧 Very humid: {humidity}%. May feel warmer."
            elif humidity > 60:
                return f"💦 Moderate humidity: {humidity}%."
            return f"😊 Low humidity: {humidity}%. Comfortable."
        
        # Wind queries
        if any(w in message_lower for w in ["wind", "windy"]):
            wind = current.get("wind_speed_kmh", 0)
            if wind > 30:
                return f"💨 Very windy at {wind} km/h! Be careful."
            elif wind > 15:
                return f"🍃 Breezy at {wind} km/h."
            return f"🌬️ Light wind at {wind} km/h."
        
        # General weather summary
        if any(w in message_lower for w in ["weather", "conditions", "today"]):
            wind = current.get("wind_speed_kmh", 0)
            humidity = current.get("humidity_percent", 0)
            return f"⛅ {city}: {condition}, {temp}°C. Wind: {wind} km/h, Humidity: {humidity}%."
        
        # Default responses
        responses = [
            f"Weather in {city}: {condition}, {temp}°C. What would you like to know?",
            f"I can help with weather info! Ask about temp, rain, wind, etc.",
            f"Current conditions: {condition}. Need specific details?"
        ]
        return random.choice(responses)
