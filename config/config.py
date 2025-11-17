import os
from dataclasses import dataclass

@dataclass
class Config:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AISQ5xY")
    GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    WEATHER_API_KEY: str = "b010b111"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    SECRET_KEY: str = "flint-weather-ai-2025"
    MAX_CONTENT_LENGTH: int = 16777216
    CACHE_DURATION: int = 600
    MAX_CACHE_SIZE: int = 500
    NOMINATIM_USER_AGENT: str = "FlintWeatherAI/1.0"
    NOMINATIM_TIMEOUT: int = 10
    MAX_RETRIES: int = 2
    BASE_DELAY: float = 2.0
    MAX_DELAY: float = 10.0
    REQUEST_TIMEOUT: int = 15
    GEMINI_RATE_LIMIT_DELAY: float = 10.0
    GEMINI_MAX_REQUESTS_PER_MINUTE: int = 5
    GEMINI_MAX_REQUESTS_PER_DAY: int = 150
    USE_GEMINI: bool = True
    GEMINI_CACHE_TTL: int = 7200
    GEMINI_MAX_OUTPUT_TOKENS: int = 350

def get_config():
    return Config()
