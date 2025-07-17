
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import requests

app = Flask(__name__)
CORS(app)

PANCHANG_API_KEY = os.environ.get("PANCHANG_API_KEY")
PANCHANG_API_URL = "https://api.prokerala.com/v2/astrology/panchang"

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
        res = requests.get(
            PANCHANG_API_URL,
            headers={"Authorization": f"Bearer {PANCHANG_API_KEY}"},
            params={"date": date, "timezone": "Asia/Kolkata", "coordinates": "28.6139,77.2090"}
        )
        astro_data = res.json()
        tithi = astro_data.get("data", {}).get("tithi", {}).get("details", {}).get("tithi_number", "unknown")
        nakshatra = astro_data.get("data", {}).get("nakshatra", {}).get("name", "unknown")
        response = f"📅 On {date}, Tithi is {tithi} and Nakshatra is {nakshatra}. It is a good day for {event.title()}."
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"response": f"Error fetching Panchang data: {str(e)}"}), 500

@app.route("/", methods=["GET"])
def home():
    return "Good Day API running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
