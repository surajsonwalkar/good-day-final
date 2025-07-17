import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import openai

app = Flask(__name__)
CORS(app)

# API Keys from environment
PANCHANG_API_KEY = os.environ.get("PANCHANG_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

PANCHANG_API_URL = "https://api.prokerala.com/v2/astrology/panchang"
LATITUDE = 28.6139   # Delhi default
LONGITUDE = 77.2090
TIMEZONE = "Asia/Kolkata"


@app.route("/check_day", methods=["POST"])
def check_day():
    data = request.get_json()
    event = data.get("event", "marriage")
    date_str = data.get("date", "today")

    if date_str == "today":
        date = datetime.now().strftime("%Y-%m-%d")
    else:
        date = date_str

    try:
        # Fetch Panchang data
        panchang_res = requests.get(
            PANCHANG_API_URL,
            headers={"Authorization": f"Bearer {PANCHANG_API_KEY}"},
            params={
                "date": date,
                "timezone": TIMEZONE,
                "coordinates": f"{LATITUDE},{LONGITUDE}"
            }
        )
        panchang_data = panchang_res.json()
        if "data" not in panchang_data:
            return jsonify({"response": "Error: Panchang data unavailable."}), 500

        tithi = panchang_data["data"].get("tithi", {}).get("details", {}).get("tithi_number", "unknown")
        nakshatra = panchang_data["data"].get("nakshatra", {}).get("name", "unknown")
        weekday = panchang_data["data"].get("weekday", {}).get("name", "unknown")
        yoga = panchang_data["data"].get("yoga", {}).get("name", "unknown")

        # Create smart GPT prompt
        prompt = f"""
Today is {date}, which has the following Panchang details:
- Tithi number: {tithi}
- Nakshatra: {nakshatra}
- Yoga: {yoga}
- Weekday: {weekday}

Based on these Hindu astrology factors, is this a good day for the event: "{event}"?
Provide a culturally relevant but concise answer.
"""

        # Call OpenAI GPT for smart reasoning
        ai_res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're an expert Vedic astrologer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        result = ai_res['choices'][0]['message']['content'].strip()
        return jsonify({"response": result})

    except Exception as e:
        return jsonify({"response": f"Error processing request: {str(e)}"}), 500


@app.route("/", methods=["GET"])
def home():
    return "✅ Good Day Smart Panchang API is running."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
