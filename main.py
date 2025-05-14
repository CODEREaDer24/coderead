#!/usr/bin/env python3
from flask import Flask, render_template, request
import logging
import requests
import os
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.route('/')
def form():
    return render_template("form.html")

def extract_sections(raw_text):
    sections = {
        "TECHNICAL": "",
        "LAYMAN": "",
        "URGENCY": "",
        "COST": "",
        "CONSEQUENCES": "",
        "TIPS": "",
        "DIY": "",
        "ENVIRONMENT": "",
        "VIDEOS": "",
        "MECHANICS": ""
    }

    current = None
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.rstrip(":").upper() in sections:
            current = line.rstrip(":").upper()
            continue
        if current:
            sections[current] += line + "\n"

    return sections

@app.route('/report', methods=['POST'])
def report():
    data = request.form.to_dict()
    customer = {
        "customer_name": data.get("name", "N/A"),
        "customer_email": data.get("email", "N/A"),
        "customer_phone": data.get("phone", "")
    }
    vehicle = {
        "vehicle_make": data.get("make", ""),
        "vehicle_model": data.get("model", ""),
        "vehicle_year": data.get("year", ""),
        "code": data.get("code", "")
    }

    prompt = f"""
You're an AI car diagnostic expert. Given this info:

Vehicle: {vehicle['vehicle_year']} {vehicle['vehicle_make']} {vehicle['vehicle_model']}
OBD2 Code: {vehicle['code']}

Respond with clearly formatted report sections like this:

TECHNICAL:
...

LAYMAN:
...

URGENCY:
72
Moderate

COST:
220

CONSEQUENCES:
...

TIPS:
- First preventative tip
- Second preventative tip

DIY:
...

ENVIRONMENT:
...

VIDEOS:
Title | URL | Description

MECHANICS:
Name | Rating | Phone
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
                    {"role": "system", "content": "You are a vehicle diagnostics expert."},
                    {"role": "user", "content": prompt}
                ]
            }
        )
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        parsed = extract_sections(content)

        report = {
            "technical": parsed["TECHNICAL"].strip(),
            "layman": parsed["LAYMAN"].strip(),
            "urgency_percent": parsed["URGENCY"].splitlines()[0].strip(),
            "urgency_label": parsed["URGENCY"].splitlines()[1].strip(),
            "cost": parsed["COST"].strip(),
            "consequences": parsed["CONSEQUENCES"].strip(),
            "tips": [t.strip("- ").strip() for t in parsed["TIPS"].splitlines() if t.strip()],
            "diy": parsed["DIY"].strip(),
            "environment": parsed["ENVIRONMENT"].strip(),
            "videos": [
                {
                    "title": v.split("|")[0].strip(),
                    "url": v.split("|")[1].strip(),
                    "description": v.split("|")[2].strip()
                }
                for v in parsed["VIDEOS"].splitlines() if "|" in v
            ],
            "mechanics": [
                {
                    "name": m.split("|")[0].strip(),
                    "rating": m.split("|")[1].strip(),
                    "phone": m.split("|")[2].strip()
                }
                for m in parsed["MECHANICS"].splitlines() if "|" in m
            ]
        }

    except Exception as e:
        logging.error("GPT fallback triggered", exc_info=True)
        report = {
            "technical": "This code means the crankshaft position sensor signal isn’t reaching the computer.",
            "layman": "Your car doesn't know how fast the engine is spinning — sensor might be broken.",
            "urgency_percent": "72",
            "urgency_label": "Urgent",
            "cost": "220",
            "consequences": "Could stall, misfire, or not start at all.",
            "tips": ["Check the crankshaft sensor", "Inspect wires and connectors"],
            "diy": "Moderate if you have basic tools.",
            "environment": "Could raise emissions due to poor timing.",
            "videos": [
                {
                    "title": "P0320 Sensor Explained",
                    "url": "https://www.youtube.com/watch?v=LSxBdj3kKYI",
                    "description": "Sensor function and failure modes"
                },
                {
                    "title": "Fix P0320 Code",
                    "url": "https://www.youtube.com/watch?v=9M1i6F4I6hU",
                    "description": "How to test and replace the crankshaft sensor"
                }
            ],
            "mechanics": [
                {"name": "Clover Auto", "rating": "4.8", "phone": "519-555-1234"},
                {"name": "Tecumseh Auto Repair", "rating": "4.6", "phone": "519-555-5678"},
                {"name": "Auto Clinic Windsor", "rating": "4.7", "phone": "519-555-9999"}
            ]
        }

    return render_template("report.html",
        generated_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        **customer,
        **vehicle,
        urgency_percent=report["urgency_percent"],
        urgency_label=report["urgency_label"],
        technical_explanation=report["technical"],
        layman_explanation=report["layman"],
        repair_cost_cad=report["cost"],
        consequences=report["consequences"],
        preventative_tips=report["tips"],
        diy_potential=report["diy"],
        environmental_impact=report["environment"],
        videos=report["videos"],
        mechanics=report["mechanics"]
    )

if __name__ == '__main__':
    app.run(debug=True)
