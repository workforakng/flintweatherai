import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

print(f"Project root: {PROJECT_ROOT}")

try:
    from config.config import get_config
    from utils.cache import ThreadSafeLRUCache
    from utils.weather import WeatherUtils
    from utils.free_weather_apis import FreeWeatherAPIs
    from utils.free_ai_apis import FreeAIAPIs
    print("All modules imported successfully")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from functools import wraps
import requests
import json
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
import time
import random
import threading
from typing import Optional, Dict, List

app = Flask(__name__, static_folder="../static", template_folder="../templates")
CORS(app)

os.makedirs("logs", exist_ok=True)

# Detailed formatter for comprehensive logging
detailed_formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s')

# Main comprehensive log - everything
overall_handler = RotatingFileHandler("logs/overall.log", maxBytes=20*1024*1024, backupCount=5)
overall_handler.setFormatter(detailed_formatter)
overall_handler.setLevel(logging.DEBUG)

# Error log
error_handler = RotatingFileHandler("logs/errors.log", maxBytes=10*1024*1024, backupCount=3)
error_handler.setFormatter(detailed_formatter)
error_handler.setLevel(logging.ERROR)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(levelname)s | %(message)s'))
console_handler.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(overall_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)

# Also log all requests
logging.getLogger().addHandler(overall_handler)

config = get_config()
app.config['SECRET_KEY'] = config.SECRET_KEY

weather_cache = ThreadSafeLRUCache(max_size=config.MAX_CACHE_SIZE)
location_cache = ThreadSafeLRUCache(max_size=config.MAX_CACHE_SIZE)

gemini_enabled = config.USE_GEMINI

class SmartRateLimiter:
    def __init__(self):
        self.last_request = {}
        self.lock = threading.Lock()
    
    def wait_if_needed(self, api_name: str, min_interval: float):
        with self.lock:
            last = self.last_request.get(api_name, 0)
            elapsed = time.time() - last
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            self.last_request[api_name] = time.time()

rate_limiter = SmartRateLimiter()
# Gemini Request Tracker for Free Tier limits
class GeminiRequestTracker:
    def __init__(self):
        self.minute_requests = []
        self.daily_requests = 0
        self.last_reset = datetime.now()
        self.lock = threading.Lock()
    
    def can_make_request(self):
        with self.lock:
            now = datetime.now()
            if now.date() != self.last_reset.date():
                self.daily_requests = 0
                self.last_reset = now
            cutoff = now.timestamp() - 60
            self.minute_requests = [t for t in self.minute_requests if t > cutoff]
            if len(self.minute_requests) >= config.GEMINI_MAX_REQUESTS_PER_MINUTE:
                return False, "minute"
            if self.daily_requests >= config.GEMINI_MAX_REQUESTS_PER_DAY:
                return False, "daily"
            return True, None
    
    def record_request(self):
        with self.lock:
            now = datetime.now()
            self.minute_requests.append(now.timestamp())
            self.daily_requests += 1

gemini_tracker = GeminiRequestTracker()


def cache_key(lat: float, lon: float) -> str:
    return f"weather_{lat}_{lon}".replace(".", "_")

def validate_coordinates(lat: float, lon: float) -> bool:
    try:
        lat = float(lat)
        lon = float(lon)
        return (-90 <= lat <= 90) and (-180 <= lon <= 180)
    except:
        return False

def sanitize_input(text: str, max_length: int = 200) -> str:
    if not isinstance(text, str):
        return ""
    text = text.replace("<", "").replace(">", "").replace('"', "")
    text = text.replace("'", "").replace("&", "").replace("\\", "")
    return text.strip()[:max_length]

def get_gemini_weather(location_info: Dict) -> Optional[Dict]:
    global gemini_enabled
    if not gemini_enabled:
        return None
    try:
        rate_limiter.wait_if_needed('gemini', config.GEMINI_RATE_LIMIT_DELAY)
        prompt = f"""Weather for {location_info.get('city')} ({location_info.get('latitude')}, {location_info.get('longitude')}).
Return ONLY JSON:
{{"condition": "Clear/Cloudy/etc", "temperature_celsius": 25.0, "feels_like_celsius": 24.0, "humidity_percent": 65, "wind_speed_kmh": 15.0, "description": "brief", "alerts": ["tip1"]}}"""
        url = f"{config.GEMINI_API_URL}?key={config.GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.5, "maxOutputTokens": 300}}
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 429:
            logger.warning("Gemini rate limit, disabling")
            gemini_enabled = False
            return None
        response.raise_for_status()
        data = response.json()
        if 'candidates' in data:
            text = data['candidates'][0]['content']['parts'][0]['text']
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                weather_data = json.loads(text[start:end])
                weather_data.update({"source": "Gemini AI", "is_real_data": False, "timestamp": datetime.now().isoformat()})
                logger.info("Gemini weather OK")
                return weather_data
    except Exception as e:
        logger.debug(f"Gemini error: {e}")
    return None

def get_location_details(lat: float, lon: float) -> Optional[Dict]:
    if not validate_coordinates(lat, lon):
        return None
    cache_k = cache_key(lat, lon)
    cached = location_cache.get(cache_k)
    if cached:
        return cached
    try:
        rate_limiter.wait_if_needed('nominatim', 1.0)
        url = f"https://nominatim.openstreetmap.org/reverse"
        params = {'format': 'json', 'lat': lat, 'lon': lon, 'zoom': 18, 'addressdetails': 1}
        headers = {'User-Agent': config.NOMINATIM_USER_AGENT}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        address = data.get('address', {})
        result = {
            'locality': address.get('suburb') or address.get('neighbourhood') or 'Unknown',
            'city': address.get('city') or address.get('town') or address.get('village') or 'Unknown City',
            'region': address.get('state', ''),
            'country': address.get('country', 'Unknown'),
            'display_name': data.get('display_name', ''),
            'latitude': lat,
            'longitude': lon
        }
        location_cache.set(cache_k, result, ttl=3600)
        return result
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        return None

def search_location(query: str) -> List[Dict]:
    query = sanitize_input(query)
    if not query:
        return []
    try:
        rate_limiter.wait_if_needed('nominatim', 1.0)
        url = "https://nominatim.openstreetmap.org/search"
        params = {'format': 'json', 'q': query, 'limit': 5, 'addressdetails': 1}
        headers = {'User-Agent': config.NOMINATIM_USER_AGENT}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        results = response.json()
        locations = []
        for result in results:
            address = result.get('address', {})
            locations.append({
                'display_name': result.get('display_name', ''),
                'latitude': float(result.get('lat', 0)),
                'longitude': float(result.get('lon', 0)),
                'city': address.get('city') or address.get('town') or address.get('village', ''),
                'country': address.get('country', '')
            })
        return locations
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []

def get_weather_tips(temp, condition, uv, wind, humidity) -> List[str]:
    tips = []
    if temp is not None:
        if temp >= 35:
            tips.append("Extreme heat! Stay indoors.")
        elif temp >= 30:
            tips.append("Very hot! Stay hydrated.")
        elif temp <= 0:
            tips.append("Freezing! Bundle up.")
        elif temp <= 10:
            tips.append("Cold. Wear warm layers.")
    if condition:
        cond = condition.lower()
        if "rain" in cond:
            tips.append("Rain expected. Bring umbrella!")
        if "storm" in cond:
            tips.append("Storm warning! Stay indoors.")
        if "snow" in cond:
            tips.append("Snow! Drive carefully.")
    if uv and uv >= 6:
        tips.append(f"High UV! Use sunscreen.")
    if wind and wind >= 40:
        tips.append("Strong winds!")
    if humidity and humidity >= 80:
        tips.append("Very humid.")
    return tips if tips else ["Weather looks good!"]

def get_weather_data(location_info: Dict) -> Dict:
    cache_k = cache_key(location_info['latitude'], location_info['longitude'])
    cached = weather_cache.get(cache_k)
    if cached:
        logger.info("Using cached weather")
        return cached
    
    gemini_weather = get_gemini_weather(location_info)
    if gemini_weather:
        weather_data = build_weather_response(gemini_weather, location_info)
        weather_data["weather_tips"].insert(0, "AI-powered from Gemini")
        weather_cache.set(cache_k, weather_data, ttl=1800)
        return weather_data
    
    free_weather = FreeWeatherAPIs.get_weather(
        location_info['latitude'],
        location_info['longitude'],
        config.WEATHER_API_KEY
    )
    weather_data = build_weather_response(free_weather, location_info)
    if free_weather.get('is_mock_data'):
        weather_data["weather_tips"].insert(0, "Simulated data")
    else:
        weather_data["weather_tips"].insert(0, f"From {free_weather.get('source')}")
    ttl = 1800 if free_weather.get('is_mock_data') else 3600
    weather_cache.set(cache_k, weather_data, ttl=ttl)
    return weather_data

def build_weather_response(current_weather: Dict, location_info: Dict) -> Dict:
    temp = current_weather.get('temperature_celsius', 0)
    return {
        "current_weather": current_weather,
        "forecast": {
            "today": f"{current_weather.get('condition', 'Unknown')}, High: {temp + 2} C",
            "tomorrow": f"Similar, High: {temp + random.randint(-2, 2)} C",
            "day_after": f"Partly {current_weather.get('condition', 'Unknown')}, High: {temp} C"
        },
        "sun_times": {"sunrise": "06:30 AM", "sunset": "06:45 PM"},
        "moon_phase": random.choice(["New Moon", "First Quarter", "Full Moon", "Last Quarter"]),
        "location": location_info,
        "weather_tips": get_weather_tips(
            temp,
            current_weather.get('condition'),
            current_weather.get('uv_index'),
            current_weather.get('wind_speed_kmh'),
            current_weather.get('humidity_percent')
        )
    }

def get_chatbot_response(message: str, weather_data: Dict) -> str:
    message = sanitize_input(message, 500)
    if not message:
        return "Please ask a question about the weather!"
    location = weather_data.get('location', {})
    current = weather_data.get('current_weather', {})
    forecast = weather_data.get('forecast', {})
    city = location.get('city', 'your location')
    country = location.get('country', '')
    temp = current.get('temperature_celsius', 0)
    condition = current.get('condition', 'unknown')
    humidity = current.get('humidity_percent', 0)
    wind = current.get('wind_speed_kmh', 0)
    feels_like = current.get('feels_like_celsius', temp)
    if gemini_enabled:
        can_request, limit_type = gemini_tracker.can_make_request()
        if not can_request:
            if limit_type == "minute":
                logger.info("Minute limit reached, waiting 8 seconds...")
                time.sleep(8)
                can_request, _ = gemini_tracker.can_make_request()
            if not can_request:
                logger.warning(f"Gemini {limit_type} limit still exceeded")
                return f"I am currently at my API limit. Current weather in {city}: {condition}, {temp} degrees C. Wind: {wind} km/h, Humidity: {humidity}%. Ask me again in a moment!"
        try:
            rate_limiter.wait_if_needed('gemini_chat', config.GEMINI_RATE_LIMIT_DELAY)
            cache_k = f"chat_{city}_{message[:50]}"
            cached = weather_cache.get(cache_k)
            if cached:
                logger.info("Using cached chat response")
                return cached
            context = f"""You are a helpful weather assistant. Current weather data for {city}, {country}:
- Temperature: {temp} degrees Celsius (feels like {feels_like} C)
- Condition: {condition}
- Humidity: {humidity} percent
- Wind: {wind} km/h
- Today forecast: {forecast.get('today', 'N/A')}
- Tomorrow forecast: {forecast.get('tomorrow', 'N/A')}

User question: {message}

Provide a natural, conversational response in 2-4 complete sentences. Include specific data from above. Finish your thoughts completely."""
            url = f"{config.GEMINI_API_URL}?key={config.GEMINI_API_KEY}"
            payload = {"contents": [{"parts": [{"text": context}]}], "generationConfig": {"temperature": 0.7, "maxOutputTokens": 300, "topP": 0.9}}
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 429:
                logger.warning("Gemini API returned 429, waiting 10 seconds...")
                time.sleep(10)
                return f"API is busy right now. But I can tell you: {city} weather is {condition}, {temp} degrees C. Try asking again!"
            response.raise_for_status()
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                try:
                    text = data['candidates'][0]['content']['parts'][0]['text']
                    logger.info("Gemini chat success")
                    gemini_tracker.record_request()
                    weather_cache.set(cache_k, text, ttl=config.GEMINI_CACHE_TTL)
                    return text.strip()
                except (KeyError, IndexError) as e:
                    logger.error(f"Gemini parse error: {e}")
            logger.warning("No valid response from Gemini")
        except Exception as e:
            logger.error(f"Gemini error: {e}")
    return FreeAIAPIs.get_chat_response(message, weather_data)

def handle_errors(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"Validation: {e}")
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {e}", exc_info=True)
            return jsonify({"error": "Internal error"}), 500
    return decorated

@app.route('/')
def index():
    return send_from_directory('../templates', 'index.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('..', 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('..', 'service-worker.js')

@app.route('/api/reverse-geocode', methods=['POST'])
@handle_errors
def reverse_geocode():
    data = request.get_json()
    if not data:
        raise ValueError("No data")
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    if not validate_coordinates(lat, lon):
        raise ValueError("Invalid coordinates")
    location = get_location_details(lat, lon)
    if not location:
        raise ValueError("Location failed")
    return jsonify(location)

@app.route('/api/search-location', methods=['POST'])
@handle_errors
def search_location_route():
    data = request.get_json()
    query = data.get('query', '').strip()
    if not query:
        raise ValueError("Query required")
    locations = search_location(query)
    return jsonify({"results": locations})

@app.route('/api/weather', methods=['POST'])
@handle_errors
def get_weather():
    data = request.get_json()
    if not data:
        raise ValueError("No data")
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    if not validate_coordinates(lat, lon):
        raise ValueError("Invalid coordinates")
    location_info = get_location_details(lat, lon)
    if not location_info:
        location_info = {'latitude': lat, 'longitude': lon, 'locality': 'Unknown', 'city': 'Unknown', 'region': '', 'country': 'Unknown'}
    weather = get_weather_data(location_info)
    return jsonify(weather)

@app.route('/api/hourly', methods=['POST'])
@app.route('/api/hourly', methods=['POST'])
@handle_errors
def get_hourly():
    data = request.get_json()
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    
    logger.info(f"Hourly forecast requested for: {lat}, {lon}")
    
    if not validate_coordinates(lat, lon):
        raise ValueError("Invalid coordinates")
    
    # Try WeatherAPI.com for real hourly data
    try:
        url = "http://api.weatherapi.com/v1/forecast.json"
        params = {
            'key': config.WEATHER_API_KEY,
            'q': f"{lat},{lon}",
            'days': 1,
            'aqi': 'no',
            'alerts': 'no'
        }
        
        logger.debug(f"Requesting hourly forecast from WeatherAPI: {params['q']}")
        response = requests.get(url, params=params, timeout=10)
        
        logger.debug(f"WeatherAPI hourly response status: {response.status_code}")
        
        if response.status_code == 200:
            api_data = response.json()
            forecast_day = api_data.get('forecast', {}).get('forecastday', [])
            
            if forecast_day and len(forecast_day) > 0:
                forecast_hours = forecast_day[0].get('hour', [])
                
                if forecast_hours:
                    hourly = []
                    for hour_data in forecast_hours:
                        time_str = hour_data.get('time', '').split()[-1] if hour_data.get('time') else '00:00'
                        hourly.append({
                            'hour': time_str,
                            'temperature_celsius': round(hour_data.get('temp_c', 20), 1),
                            'precipitation_chance': int(hour_data.get('chance_of_rain', 0)),
                            'condition': hour_data.get('condition', {}).get('text', 'Clear'),
                            'humidity': hour_data.get('humidity', 50),
                            'wind_kph': round(hour_data.get('wind_kph', 0), 1)
                        })
                    
                    logger.info(f"Returning {len(hourly)} hours of real forecast data")
                    return jsonify({"hourly_forecast": hourly})
        
        logger.warning(f"WeatherAPI returned {response.status_code}: {response.text[:200]}")
    
    except requests.exceptions.Timeout:
        logger.error("WeatherAPI timeout for hourly forecast")
    except requests.exceptions.RequestException as e:
        logger.error(f"WeatherAPI request error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in hourly forecast: {e}", exc_info=True)
    
    # Fallback to realistic mock data
    logger.warning("Using fallback mock hourly data")
    hourly = []
    current_hour = datetime.now().hour
    base_temp = 21
    
    for i in range(24):
        hour_num = (current_hour + i) % 24
        # Temperature curve: cooler at night, warmer at 2-3 PM
        temp_variation = -5 * abs(hour_num - 14) / 14 + 3
        temp = base_temp + temp_variation + random.uniform(-1, 1)
        
        hourly.append({
            'hour': f"{hour_num:02d}:00",
            'temperature_celsius': round(temp, 1),
            'precipitation_chance': random.randint(0, 30),
            'condition': random.choice(['Clear', 'Partly Cloudy', 'Cloudy'])
        })
    
    return jsonify({"hourly_forecast": hourly})


@app.route('/api/forecast', methods=['POST'])
@handle_errors
def get_forecast():
    data = request.get_json()
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    
    logger.info(f"7-day forecast requested for: {lat}, {lon}")
    
    if not validate_coordinates(lat, lon):
        raise ValueError("Invalid coordinates")
    
    try:
        url = "http://api.weatherapi.com/v1/forecast.json"
        params = {
            'key': config.WEATHER_API_KEY,
            'q': f"{lat},{lon}",
            'days': 7,
            'aqi': 'yes',
            'alerts': 'yes'
        }
        
        logger.debug(f"Requesting 7-day forecast from WeatherAPI")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            api_data = response.json()
            forecast_days = api_data.get('forecast', {}).get('forecastday', [])
            
            if forecast_days:
                days = []
                day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                
                for day_data in forecast_days:
                    date_obj = datetime.strptime(day_data.get('date', ''), '%Y-%m-%d')
                    day_name = day_names[date_obj.weekday()]
                    day_info = day_data.get('day', {})
                    
                    days.append({
                        'day': day_name,
                        'date': day_data.get('date'),
                        'max_temp_c': round(day_info.get('maxtemp_c', 25), 1),
                        'min_temp_c': round(day_info.get('mintemp_c', 15), 1),
                        'condition': day_info.get('condition', {}).get('text', 'Clear'),
                        'icon': day_info.get('condition', {}).get('icon', ''),
                        'rain_chance': int(day_info.get('daily_chance_of_rain', 0)),
                        'snow_chance': int(day_info.get('daily_chance_of_snow', 0)),
                        'avg_humidity': int(day_info.get('avghumidity', 50)),
                        'max_wind_kph': round(day_info.get('maxwind_kph', 10), 1)
                    })
                
                # Get AQI data
                current = api_data.get('current', {})
                air_quality = current.get('air_quality', {})
                
                aqi_data = {
                    'us_epa_index': air_quality.get('us-epa-index', 1),
                    'gb_defra_index': air_quality.get('gb-defra-index', 1),
                    'pm2_5': round(air_quality.get('pm2_5', 0), 1),
                    'pm10': round(air_quality.get('pm10', 0), 1),
                    'co': round(air_quality.get('co', 0), 1),
                    'no2': round(air_quality.get('no2', 0), 1),
                    'o3': round(air_quality.get('o3', 0), 1),
                    'so2': round(air_quality.get('so2', 0), 1)
                }
                
                logger.info(f"Returning {len(days)} days of real forecast")
                return jsonify({
                    "forecast": days,
                    "air_quality": aqi_data
                })
        
        logger.warning(f"WeatherAPI returned {response.status_code}")
    
    except Exception as e:
        logger.error(f"7-day forecast error: {e}", exc_info=True)
    
    # Fallback mock data
    logger.warning("Using mock 7-day forecast")
    days = []
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    today = datetime.now()
    
    for i in range(7):
        day_date = today + timedelta(days=i)
        days.append({
            'day': day_names[day_date.weekday()],
            'date': day_date.strftime('%Y-%m-%d'),
            'max_temp_c': round(20 + random.uniform(-5, 10), 1),
            'min_temp_c': round(15 + random.uniform(-3, 5), 1),
            'condition': random.choice(['Clear', 'Partly Cloudy', 'Cloudy', 'Light Rain']),
            'rain_chance': random.randint(0, 60),
            'snow_chance': 0,
            'avg_humidity': random.randint(40, 80),
            'max_wind_kph': round(random.uniform(5, 25), 1)
        })
    
    return jsonify({
        "forecast": days,
        "air_quality": {
            'us_epa_index': 1,
            'pm2_5': 10.0,
            'pm10': 15.0
        }
    })

@app.route('/api/chatbot', methods=['POST'])
@handle_errors
def chatbot():
    data = request.get_json()
    message = data.get('message', '').strip()
    weather_data = data.get('weather_data', {})
    if not message:
        raise ValueError("Message required")
    if not weather_data:
        return jsonify({"response": "Please load weather data first!"}), 200
    response_text = get_chatbot_response(message, weather_data)
    return jsonify({"response": response_text})

@app.route('/api/cache-clear', methods=['POST'])
@handle_errors
def clear_cache_route():
    weather_cache.clear()
    location_cache.clear()
    return jsonify({"message": "Cache cleared"})

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "FlintWeatherAI v1.0",
        "cache_stats": {"weather": weather_cache.size(), "location": location_cache.size()},
        "gemini_enabled": gemini_enabled
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal error"}), 500

if __name__ == '__main__':
    logger.info("="*70)
    logger.info("FlintWeatherAI v1.0 Starting")
    logger.info("="*70)
    logger.info(f"Gemini: {'Enabled' if gemini_enabled else 'Disabled'}")
    logger.info(f"Weather API: {'Configured' if config.WEATHER_API_KEY else 'Not configured'}")
    logger.info("="*70)
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)
    os.makedirs("static/images", exist_ok=True)
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)