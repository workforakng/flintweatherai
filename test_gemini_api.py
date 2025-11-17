import requests
import time

api_key = "AIzaSyDQ5xYoZurnsQ7w-sW28pTgPU8IeBH2q3g"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

print("Testing Gemini API...")
print("Waiting 15 seconds...")
time.sleep(15)

payload = {"contents": [{"parts": [{"text": "Say hello"}]}], "generationConfig": {"maxOutputTokens": 10}}

try:
    response = requests.post(url, json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("SUCCESS!")
        print(f"Response: {data["candidates"][0]["content"]["parts"][0]["text"]}")
    elif response.status_code == 429:
        print("RATE LIMITED - Wait 60 seconds")
    else:
        print(f"Error: {response.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")
