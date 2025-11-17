#!/data/data/com.termux/files/usr/bin/bash

echo "=========================================="
echo "  🌤️  FlintWeatherAI Server Startup"
echo "=========================================="
echo ""

cd ~/weather/FlintWeatherAI || exit 1

if ! command -v python &> /dev/null; then
    echo "❌ Python not found!"
    exit 1
fi

echo "🐍 Python: $(python --version)"
echo ""

echo "📦 Checking dependencies..."
python -c "import flask, requests, google.generativeai" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ All dependencies installed"
else
    echo "❌ Missing dependencies!"
    echo "Install with: pip install -r requirements.txt"
    exit 1
fi

echo ""
echo "📁 Checking project structure..."
required_files=(
    "config/__init__.py"
    "config/config.py"
    "utils/__init__.py"
    "utils/cache.py"
    "utils/weather.py"
    "utils/free_weather_apis.py"
    "utils/free_ai_apis.py"
    "app/main.py"
    "templates/index.html"
    "static/css/style.css"
    "static/js/app.js"
)

missing_files=0
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing: $file"
        missing_files=$((missing_files + 1))
    fi
done

if [ $missing_files -gt 0 ]; then
    echo ""
    echo "❌ $missing_files required file(s) missing!"
    exit 1
fi

echo "✅ All required files present"
echo ""

echo "🌐 Network Information:"
echo "   Local:   http://localhost:8000"
ip_addr=$(ifconfig 2>/dev/null | grep -oP 'inet K[d.]+' | grep -v '127.0.0.1' | head -1)
if [ -n "$ip_addr" ]; then
    echo "   Network: http://$ip_addr:8000"
fi
echo ""

echo "🚀 Starting FlintWeatherAI..."
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app/main.py

echo ""
echo "Server stopped."
