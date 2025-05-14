#!/usr/bin/env python3
from flask import Flask, render_template, request
import logging
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def validate_url(url):
    return url.startswith("https://") and "youtube.com" in url

@app.route('/')
def form():
    return render_template("form.html")

@app.route('/report', methods=['POST'])
def report():
    data = request.form.to_dict()

    customer = {
        "customer_name": data.get("name", "N/A"),
        "customer_email": data.get("email", "N/A"),
        "customer_phone": data.get("phone", "")
    }
    vehicle = {
        "vehicle_make": data.get("make", "").capitalize(),
        "vehicle_model": data.get("model", "").upper(),
        "vehicle_year": data.get("year", ""),
        "code": data.get("code", "").upper()
    }

    prompt = f"""
You are an AI assistant for an automotive diagnostics app.

Return JSON with:
- technical_explanation
- layman_explanation
- urgency_percent
- urgency_label
- repair_cost_cad
- consequences
- preventative_tips (list)
- diy_potential
- environmental_impact (score or sentence)
- videos (list of title, url, description)
- mechanics (list of name, rating, phone)

OBD2 Code: {vehicle['code']}
Vehicle: {vehicle['vehicle_year']} {vehicle['vehicle_make']} {vehicle['vehicle_model']}
"""

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a JSON-generating diagnostics AI."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        resp.raise_for_status()
        result = resp.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not content.strip().startswith("{"):
            raise ValueError("OpenAI returned empty or invalid JSON")
        analysis = json.loads(content)
    except Exception as e:
        logging.error("Failed to parse OpenAI response", exc_info=True)
        return render_template("form.html", error="OpenAI failed to generate a response. Please check your API key or try again later.")

    urgency = int(analysis.get("urgency_percent", 0))
    label = analysis.get("urgency_label", "Unknown")
    tech = analysis.get("technical_explanation", "No data")
    lay = analysis.get("layman_explanation", "No data")
    cost = analysis.get("repair_cost_cad", "0")
    cons = analysis.get("consequences", "None specified")
    tips = analysis.get("preventative_tips", [])
    diy = analysis.get("diy_potential", "Not recommended")
    env = analysis.get("environmental_impact", "Not assessed")

    videos = []
    for video in analysis.get("videos", []):
        if validate_url(video.get("url", "")):
            videos.append({
                "title": video.get("title", "Video"),
                "url": video.get("url"),
                "description": video.get("description", "")
            })

    fallback_mechanics = [
        {"name": "Clover Auto", "rating": "4.7", "phone": "519-555-1234"},
        {"name": "Tecumseh Auto Repair", "rating": "4.6", "phone": "519-555-5678"}
    ]
    gpt_mechanics = analysis.get("mechanics", [])
    mechanics = fallback_mechanics + [
        m for m in gpt_mechanics if m.get("name") not in [fm["name"] for fm in fallback_mechanics]
    ]

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
