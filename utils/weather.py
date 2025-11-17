from typing import Dict

class WeatherUtils:
    """Weather utility functions"""
    
    @staticmethod
    def get_weather_icon(condition: str) -> str:
        """Get Font Awesome icon class for weather condition"""
        if not condition:
            return "fa-cloud"
        
        condition = condition.lower()
        if 'clear' in condition or 'sunny' in condition:
            return "fa-sun"
        elif 'rain' in condition:
            return "fa-cloud-rain"
        elif 'snow' in condition:
            return "fa-snowflake"
        elif 'cloud' in condition:
            return "fa-cloud"
        elif 'storm' in condition or 'thunder' in condition:
            return "fa-bolt"
        elif 'fog' in condition or 'mist' in condition:
            return "fa-smog"
        elif 'wind' in condition:
            return "fa-wind"
        return "fa-cloud"
    
    @staticmethod
    def get_uv_index_level(uv: float) -> Dict[str, str]:
        """Get UV index level information"""
        if uv <= 2:
            return {
                "level": "Low",
                "color": "#4ade80",
                "recommendation": "No protection needed"
            }
        elif uv <= 5:
            return {
                "level": "Moderate",
                "color": "#facc15",
                "recommendation": "Wear sunscreen"
            }
        elif uv <= 7:
            return {
                "level": "High",
                "color": "#fb923c",
                "recommendation": "Protection essential"
            }
        elif uv <= 10:
            return {
                "level": "Very High",
                "color": "#ef4444",
                "recommendation": "Extra protection required"
            }
        else:
            return {
                "level": "Extreme",
                "color": "#a855f7",
                "recommendation": "Avoid sun exposure"
            }
    
    @staticmethod
    def celsius_to_fahrenheit(celsius: float) -> float:
        """Convert Celsius to Fahrenheit"""
        return round((celsius * 9/5) + 32, 1)
    
    @staticmethod
    def get_wind_direction_arrow(direction: str) -> str:
        """Get arrow emoji for wind direction"""
        directions = {
            'N': '↑', 'NNE': '↗', 'NE': '↗', 'ENE': '↗',
            'E': '→', 'ESE': '↘', 'SE': '↘', 'SSE': '↘',
            'S': '↓', 'SSW': '↙', 'SW': '↙', 'WSW': '↙',
            'W': '←', 'WNW': '↖', 'NW': '↖', 'NNW': '↖'
        }
        return directions.get(direction, '•')
