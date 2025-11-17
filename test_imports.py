#!/usr/bin/env python3
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

print("=" * 50)
print("Testing FlintWeatherAI Imports")
print("=" * 50)
print()

tests = [
    ("Flask", "flask"),
    ("Flask-CORS", "flask_cors"),
    ("Requests", "requests"),
    ("Python-DateUtil", "dateutil"),
    ("Google GenAI", "google.generativeai"),
    ("Config Module", "config.config"),
    ("Cache Module", "utils.cache"),
    ("Weather Module", "utils.weather"),
    ("Weather APIs Module", "utils.free_weather_apis"),
    ("AI APIs Module", "utils.free_ai_apis"),
]

failed = 0
for name, module in tests:
    try:
        __import__(module)
        print(f"✅ {name:20s} OK")
    except ImportError as e:
        print(f"❌ {name:20s} FAILED: {e}")
        failed += 1

print()
print("=" * 50)
if failed == 0:
    print("✅ All imports successful! Ready to start.")
    sys.exit(0)
else:
    print(f"❌ {failed} import(s) failed!")
    sys.exit(1)
