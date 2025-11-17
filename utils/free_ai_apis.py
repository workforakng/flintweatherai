import random
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class FreeAIAPIs:
    """Enhanced fallback AI with agriculture and general knowledge"""
    
    @staticmethod
    def get_enhanced_chat_response(message: str, weather_data: Dict) -> str:
        """Enhanced chatbot response with agriculture support"""
        message_lower = message.lower()
        current = weather_data.get("current_weather", {})
        location = weather_data.get("location", {})
        
        temp = current.get("temperature_celsius", 0)
        temp_f = current.get("temperature_fahrenheit", 0)
        condition = current.get("condition", "").lower()
        city = location.get("city", "your location")
        humidity = current.get("humidity_percent", 0)
        wind = current.get("wind_speed_kmh", 0)
        uv = current.get("uv_index", 0)
        
        # AGRICULTURE / VEGETATION QUESTIONS
        if any(word in message_lower for word in ['grow', 'plant', 'crop', 'farm', 'vegetat', 'agricultur', 'garden', 'cultivat', 'harvest', 'sow', 'seed']):
            return FreeAIAPIs._get_agriculture_response(temp, humidity, city, condition)
        
        # IDENTITY QUESTIONS
        elif any(word in message_lower for word in ['who are you', 'what are you', 'your name', 'introduce yourself', 'what can you do']):
            return "I'm FlintWeatherAI, your intelligent weather assistant with expertise in meteorology, agriculture, and general knowledge! I can help with weather forecasts, crop recommendations, farming advice, and answer your questions. How can I assist you today?"
        
        # GENERAL KNOWLEDGE (sample - Gemini handles most)
        elif 'capital' in message_lower and 'france' in message_lower:
            return "Paris is the capital and largest city of France, known for the Eiffel Tower, Louvre Museum, and rich cultural heritage."
        
        # TEMPERATURE QUESTIONS
        elif any(word in message_lower for word in ['temp', 'hot', 'cold', 'warm', 'heat', 'degree']):
            feels_text = "very hot" if temp > 35 else "quite warm" if temp > 30 else "pleasant" if temp > 20 else "cool" if temp > 10 else "cold"
            advice = "Stay hydrated and avoid sun!" if temp > 35 else "Great weather!" if 20 <= temp <= 28 else "Dress warmly!" if temp < 10 else ""
            return f"It's currently {temp}°C ({temp_f}°F) in {city}, which feels {feels_text}. Conditions: {condition}. {advice}"
        
        # RAIN / PRECIPITATION
        elif any(word in message_lower for word in ['rain', 'precipitation', 'wet', 'umbrella', 'shower']):
            if 'rain' in condition or 'drizzle' in condition:
                return f"🌧️ Yes, it's {condition} in {city} right now. Humidity is {humidity}%. Definitely bring an umbrella!"
            else:
                return f"☀️ No rain expected right now in {city}. Current conditions: {condition}. Humidity is {humidity}%."
        
        # WIND QUESTIONS
        elif 'wind' in message_lower:
            wind_desc = "very strong" if wind > 40 else "strong" if wind > 30 else "moderate" if wind > 15 else "light"
            return f"Wind speed in {city} is {wind} km/h ({wind_desc}). {f'Be careful outdoors!' if wind > 30 else 'Conditions are manageable.'} Current weather: {condition}."
        
        # UV / SUN
        elif any(word in message_lower for word in ['sun', 'uv', 'sunburn', 'sunscreen', 'sunny']):
            if uv >= 8:
                return f"⚠️ UV index is {uv} (very high) in {city}. Wear sunscreen SPF 30+, sunglasses, and protective clothing!"
            elif uv >= 6:
                return f"☀️ UV index is {uv} (high) in {city}. Use sunscreen and avoid prolonged sun exposure!"
            elif uv >= 3:
                return f"🌤️ UV index is {uv} (moderate) in {city}. Consider sunscreen for extended outdoor activities."
            else:
                return f"🌥️ UV index is {uv} (low) in {city}. No special protection needed."
        
        # HUMIDITY
        elif 'humid' in message_lower:
            humid_desc = "extremely humid (uncomfortable)" if humidity > 85 else "very humid" if humidity > 70 else "moderately humid" if humidity > 50 else "comfortable"
            return f"Humidity in {city} is {humidity}% ({humid_desc}). Temperature: {temp}°C with {condition}."
        
        # OUTDOOR ACTIVITIES
        elif any(word in message_lower for word in ['jogging', 'running', 'walking', 'hiking', 'outdoor', 'outside']):
            if temp > 35:
                return f"🥵 It's {temp}°C, too hot for strenuous outdoor activities. Try early morning or evening, stay hydrated!"
            elif 'rain' in condition or 'storm' in condition:
                return f"🌧️ It's {condition}, not ideal for outdoor activities. Wait for weather to clear!"
            elif 15 <= temp <= 28:
                return f"✅ Perfect weather for outdoor activities! {temp}°C with {condition}. Enjoy!"
            elif temp < 10:
                return f"🥶 It's {temp}°C, quite cold. Dress in warm layers if going outside!"
            else:
                return f"Weather is {condition}, {temp}°C. Conditions are acceptable for outdoor activities."
        
        # DEFAULT WEATHER SUMMARY
        else:
            responses = [
                f"Weather in {city}: {condition}, {temp}°C. Humidity {humidity}%, wind {wind} km/h, UV index {uv}. What would you like to know?",
                f"I can help with weather, agriculture, or general questions! Current conditions in {city}: {condition}, {temp}°C. Ask me anything!",
                f"Current conditions: {condition}, {temp}°C in {city}. Need specific weather details, crop advice, or have any other questions?"
            ]
            return random.choice(responses)
    
    @staticmethod
    def _get_agriculture_response(temp: float, humidity: int, city: str, condition: str) -> str:
        """Generate agriculture-specific recommendations based on climate"""
        
        # Tropical Climate (>27°C, high humidity >70%)
        if temp > 27 and humidity > 70:
            crops = "rice, sugarcane, bananas, papayas, mangoes, pineapples, coconuts, cassava, yams"
            climate = "tropical (hot & humid)"
            season = "Year-round with monsoon cycles"
            advice = "High temperature and humidity are ideal for tropical crops. Ensure proper drainage to prevent waterlogging. Watch for fungal diseases in humid conditions."
        
        # Hot Dry Climate (>30°C, low humidity <40%)
        elif temp > 30 and humidity < 40:
            crops = "dates, olives, millet, sorghum, certain cacti, drought-resistant vegetables (okra, eggplant)"
            climate = "hot arid/semi-arid"
            season = "Cooler months for most crops"
            advice = "Focus on drought-resistant crops. Implement drip irrigation to conserve water. Mulching helps retain soil moisture. Morning watering is best."
        
        # Warm Temperate (20-27°C, moderate humidity 50-70%)
        elif 20 <= temp <= 27:
            crops = "wheat, corn, soybeans, tomatoes, peppers, cucumbers, beans, squash, sunflowers"
            climate = "warm temperate (ideal growing conditions)"
            season = "Late spring through early fall"
            advice = "Perfect conditions for a wide variety of crops. Practice crop rotation to maintain soil health. Regular watering during dry spells."
        
        # Cool Temperate (10-20°C, moderate humidity)
        elif 10 <= temp < 20:
            crops = "barley, oats, potatoes, carrots, lettuce, cabbage, broccoli, peas, spinach, radishes"
            climate = "cool temperate"
            season = "Spring and fall (cool season crops)"
            advice = "Ideal for cool-season vegetables and grains. Protect young plants from late frosts with row covers. These crops can tolerate light frost."
        
        # Cold Climate (<10°C)
        elif temp < 10:
            crops = "winter wheat, winter rye, kale, brussels sprouts, hardy greens (if above freezing), garlic (plant in fall)"
            climate = "cold (limited growing season)"
            season = "Very short summer window; focus on cold-hardy varieties"
            advice = "Limited growing season. Consider greenhouses or cold frames for extended growing. Focus on frost-resistant crops. Start seeds indoors."
        
        # Moderate conditions (fallback)
        else:
            crops = "lettuce, herbs (basil, parsley), green beans, zucchini, strawberries"
            climate = "moderate"
            season = "Spring-Summer"
            advice = "Good conditions for various vegetables. Monitor temperature changes and adjust watering accordingly."
        
        return f"""🌾 **Agriculture Recommendations for {city}**

**Climate Zone**: {climate}
**Current Conditions**: {temp}°C, {humidity}% humidity, {condition}

**Recommended Crops**: {crops}

**Best Growing Season**: {season}

**Farming Advice**: {advice}

💡 **Quick Tips**:
- Soil pH: Most vegetables prefer 6.0-7.0
- Watering: {"Daily in hot weather" if temp > 30 else "Every 2-3 days" if temp > 20 else "Weekly or as needed"}
- Fertilizer: Apply organic compost or balanced NPK fertilizer

Would you like specific planting schedules, pest control advice, or irrigation tips?"""
    
    @staticmethod
    def get_chat_response(message: str, weather_data: Dict) -> str:
        """Legacy method - redirects to enhanced version"""
        return FreeAIAPIs.get_enhanced_chat_response(message, weather_data)
