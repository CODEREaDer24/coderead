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

    # Build GPT prompt (text output, not JSON)
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

    fallback_report = {
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

        # Parse fields from raw text
        def get(section):
            try:
                lines = content.split(section + ":")[1].split("\n")
                if section == "URGENCY":
                    return lines[1].strip(), lines[2].strip()
                if section == "VIDEOS":
                    vids = []
                    for line in lines[1:]:
                        if "|" in line:
                            title, url, desc = [x.strip() for x in line.split("|")]
                            vids.append({"title": title, "url": url, "description": desc})
                    return vids
                if section == "MECHANICS":
                    mechs = []
                    for line in lines[1:]:
                        if "|" in line:
                            name, rating, phone = [x.strip() for x in line.split("|")]
                            mechs.append({"name": name, "rating": rating, "phone": phone})
                    return mechs
                if section == "TIPS":
                    return [x.strip("- ").strip() for x in lines if x.strip().startswith("-")]
                return "\n".join(lines[1:]).strip()
            except Exception as e:
                logging.warning(f"Parse error for section {section}: {e}")
                return ""

        report = {
            "technical": get("TECHNICAL"),
            "layman": get("LAYMAN"),
            "urgency_percent": get("URGENCY")[0],
            "urgency_label": get("URGENCY")[1],
            "cost": get("COST"),
            "consequences": get("CONSEQUENCES"),
            "tips": get("TIPS"),
            "diy": get("DIY"),
            "environment": get("ENVIRONMENT"),
            "videos": get("VIDEOS"),
            "mechanics": get("MECHANICS"),
        }

    except Exception as e:
        logging.error("GPT fallback triggered", exc_info=True)
        report = fallback_report

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
