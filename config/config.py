import os
from dataclasses import dataclass
from pathlib import Path

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # python-dotenv not installed, use environment variables only

@dataclass
class Config:
    """Application configuration with environment variable support"""
    
    # API Keys - prefer .env, then environment variables, finally defaults
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AIzaSyDQ5xYoZurnsQ7w-sW28pTgPU8IeBH2q3g")
    GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "b010b4bbd1524f6c92c192501251111")
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "flint-weather-ai-2025-secure-key")
    
    # Request limits
    MAX_CONTENT_LENGTH: int = 16777216
    REQUEST_TIMEOUT: int = 15
    MAX_RETRIES: int = 2
    BASE_DELAY: float = 2.0
    MAX_DELAY: float = 10.0
    
    # Cache settings
    CACHE_DURATION: int = 600
    MAX_CACHE_SIZE: int = 500
    GEMINI_CACHE_TTL: int = 7200
    
    # Nominatim (Location search)
    NOMINATIM_USER_AGENT: str = "FlintWeatherAI/1.0"
    NOMINATIM_TIMEOUT: int = 10
    
    # Gemini API settings
    USE_GEMINI: bool = os.getenv("USE_GEMINI", "True").lower() == "true"
    GEMINI_RATE_LIMIT_DELAY: float = 10.0
    GEMINI_MAX_REQUESTS_PER_MINUTE: int = 5
    GEMINI_MAX_REQUESTS_PER_DAY: int = 1500
    GEMINI_MAX_OUTPUT_TOKENS: int = 500

def get_config():
    """Get application configuration instance"""
    return Config()
