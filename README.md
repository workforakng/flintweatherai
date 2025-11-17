# 🌤️ FlintWeatherAI

> Intelligent weather forecasting with AI-powered chatbot, agriculture recommendations, and real-time forecasts.

## Features

- **Real-time Weather**: Current conditions, hourly & 7-day forecasts
- **AI Chatbot**: Powered by Gemini API - answers weather, agriculture, and general questions
- **Agriculture Advice**: Crop recommendations based on climate conditions
- **Multi-source Data**: WeatherAPI.com, Open-Meteo with intelligent fallbacks
- **Air Quality Index**: PM2.5, PM10, and AQI monitoring
- **PWA Support**: Install as mobile/desktop app
- **Dark Mode**: Beautiful light/dark themes

## Live Demo

- **Production**: [https://flintweatherai.onrender.com](https://flintweatherai.onrender.com)
- **GitHub Pages**: [https://workforakng.github.io/flintweatherai](https://workforakng.github.io/flintweatherai)

## Tech Stack

- **Backend**: Python 3.10+, Flask, Gunicorn
- **Frontend**: Vanilla JavaScript, CSS3
- **APIs**: Gemini AI, WeatherAPI.com, Open-Meteo, Nominatim
- **Deployment**: Render.com, GitHub Pages
- **Caching**: Thread-safe LRU cache

## Local Setup


Clone repositorygit clone https://github.com/workforakng/flintweatherai.git
cd flintweatheraiCreate virtual environmentpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activateInstall dependenciespip install -r requirements.txtSet environment variables (optional)export GEMINI_API_KEY="your-key-here"
export WEATHER_API_KEY="your-key-here"Run serverpython app/main.py
Visit: `http://localhost:8000`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Included (limited) |
| `WEATHER_API_KEY` | WeatherAPI.com key | Included (limited) |
| `PORT` | Server port | 8000 |
| `DEBUG` | Debug mode | False |

## Chatbot Capabilities

The AI chatbot can answer:
- ✅ **Weather questions**: "What's the temperature?", "Will it rain today?"
- ✅ **Agriculture**: "What crops can I grow here?", "Is it good for planting tomatoes?"
- ✅ **General knowledge**: "Who are you?", "What's the capital of France?"
- ✅ **Activity advice**: "Can I go jogging today?"

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/weather` | POST | Current weather data |
| `/api/hourly` | POST | 24-hour forecast |
| `/api/forecast` | POST | 7-day forecast + AQI |
| `/api/chatbot` | POST | AI chatbot responses |
| `/api/search-location` | POST | Location search |
| `/health` | GET | Service health check |

## Project Structure
FlintWeatherAI/
├── app/
│   └── main.py          # Flask application
├── config/
│   └── config.py        # Configuration
├── utils/
│   ├── cache.py         # Thread-safe caching
│   ├── weather.py       # Weather utilities
│   ├── free_weather_apis.py  # Weather API integrations
│   └── free_ai_apis.py  # AI chatbot fallbacks
├── static/              # Frontend assets
├── templates/           # HTML templates
├── docs/                # GitHub Pages
└── requirements.txt     # Python dependencies
## Contributing

Pull requests are welcome! For major changes, please open an issue first.

## License

MIT License - feel free to use for personal or commercial projects.

## Author

**AkNG** - [GitHub](https://github.com/workforakng)

---

⭐ Star this repo if you find it useful!
