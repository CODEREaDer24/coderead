#!/usr/bin/env python3
from flask import Flask, render_template, request
import logging
import requests
import os
import json
from datetime import datetime
import hashlib

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Securely load the API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logging.warning("No OpenAI API key detected. Running in demo fallback mode.")
else:
    logging.info("OpenAI API key loaded successfully.")

# In-memory cache to avoid duplicate API calls
cache = {}

def get_cache_key(code, year, make, model):
    raw = f"{code}|{year}|{make}|{model}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()

def validate_url(url):
    return url.startswith("https://") and "youtube.com" in url

@app.route('/')
def form():
    return render_template("form.html")

@app.route('/report', methods=['POST'])
def report():
    form_data = request.form.to_dict()

    # Extract customer and vehicle info
    customer = {
        "customer_name": form_data.get("name", "N/A"),
        "customer_email": form_data.get("email", "N/A"),
        "customer_phone": form_data.get("phone", "")
    }
    vehicle = {
        "vehicle_make": form_data.get("make", "").capitalize(),
        "vehicle_model": form_data.get("model", "").upper(),
        "vehicle_year": form_data.get("year", ""),
        "code": form_data.get("code", "").upper()
    }

    # Caching logic
    cache_key = get_cache_key(vehicle["code"], vehicle["vehicle_year"], vehicle["vehicle_make"], vehicle["vehicle_model"])

    if cache_key in cache:
        logging.info(f"Using cached report for {vehicle['code']} on {vehicle['vehicle_make']} {vehicle['vehicle_model']}")
        analysis = cache[cache_key]
    elif not OPENAI_API_KEY:
        # Demo fallback mode
        analysis = {
            "technical_explanation": "This is demo data because no API key is configured.",
            "layman_explanation": "Your car isn’t getting the right signal from one of its engine sensors.",
            "urgency_percent": 72,
            "urgency_label": "Urgent",
            "repair_cost_cad": "240",
            "consequences": "Risk of stalling or failure to start.",
            "preventative_tips": [
                "Check crankshaft position sensor",
                "Inspect engine wiring harness"
            ],
            "diy_potential": "Moderate",
            "environmental_impact": "Increased emissions due to poor timing",
            "videos": [
                {
                    "title": "Fix Crankshaft Sensor",
                    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "description": "Walkthrough on replacing a sensor"
                }
            ],
            "mechanics": []
        }
    else:
        # Build prompt for OpenAI
        prompt = f"""
You are an AI assistant for a car diagnostics app. Return valid JSON with the following keys:
- technical_explanation
- layman_explanation
- urgency_percent
- urgency_label
- repair_cost_cad
- consequences
- preventative_tips (list)
- diy_potential
- environmental_impact
- videos (list: title, url, description)
- mechanics (list: name, rating, phone)

OBD2 Code: {vehicle['code']}
Vehicle: {vehicle['vehicle_year']} {vehicle['vehicle_make']} {vehicle['vehicle_model']}
"""

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a JSON-generating diagnostics AI."},
                        {"role": "user", "content": prompt}
                    ]
                }
            )

            response.raise_for_status()
            raw = response.json()
            content = raw.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content.strip().startswith("{"):
                raise ValueError("Invalid OpenAI response format")
            analysis = json.loads(content)
            cache[cache_key] = analysis

        except Exception as e:
            logging.error("OpenAI error:", exc_info=True)
            return render_template("form.html", error="OpenAI failed to generate a response. Try again or check API key.")

    # Sanitize/prepare report values
    urgency = int(analysis.get("urgency_percent", 0))
    label = analysis.get("urgency_label", "Unknown")
    tech = analysis.get("technical_explanation", "No data")
    lay = analysis.get("layman_explanation", "No data")
    cost = analysis.get("repair_cost_cad", "0")
    cons = analysis.get("consequences", "None specified")
    tips = analysis.get("preventative_tips", [])
    diy = analysis.get("diy_potential", "Not recommended")
    env = analysis.get("environmental_impact", "Not assessed")

    # Clean video links
    videos = []
    for v in analysis.get("videos", []):
        if validate_url(v.get("url", "")):
            videos.append({
                "title": v.get("title", "Video"),
                "url": v.get("url"),
                "description": v.get("description", "")
            })

    # Fallback mechanics + GPT-based
    fallback_mechs = [
        {"name": "Clover Auto", "rating": "4.7", "phone": "519-555-1234"},
        {"name": "Tecumseh Auto Repair", "rating": "4.6", "phone": "519-555-5678"}
    ]
    gpt_mechs = analysis.get("mechanics", [])
    mechanics = fallback_mechs + [m for m in gpt_mechs if m.get("name") not in [f["name"] for f in fallback_mechs]]

    return render_template("report.html",
        generated_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        **customer,
        **vehicle,
        urgency_percent=urgency,
        urgency_label=label,
        technical_explanation=tech,
        layman_explanation=lay,
        repair_cost_cad=cost,
        consequences=cons,
        preventative_tips=tips,
        diy_potential=diy,
        environmental_impact=env,
        videos=videos,
        mechanics=mechanics
    )

if __name__ == '__main__':
    app.run(debug=True)
