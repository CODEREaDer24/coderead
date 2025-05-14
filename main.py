from flask import Flask, render_template, request
import logging
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def clean_url(url):
    if not isinstance(url, str):
        return '#'
    url = url.strip().split()[0].rstrip('.')
    return url if url.startswith('http') else '#'

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/report", methods=["POST"])
def report():
    data = request.form.to_dict()

    customer = {
        'customer_name': data.get('name', 'N/A'),
        'customer_email': data.get('email', 'N/A'),
        'customer_phone': data.get('phone', 'N/A')
    }
    vehicle = {
        'vehicle_make': data.get('make', '').capitalize(),
        'vehicle_model': data.get('model', '').upper(),
        'vehicle_year': data.get('year', ''),
        'code': data.get('code', '').upper()
    }

    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "Return valid JSON with keys: technical_explanation, layman_explanation, urgency_percent, urgency_label, repair_cost_cad, consequences, preventative_tips (list), diy_potential, environmental_impact, video_explanation_url, video_diy_url, video_consequences_url, mechanics (list of {name,rating,phone})"},
            {"role": "user", "content": f"OBD2 code {vehicle['code']} on a {vehicle['vehicle_year']} {vehicle['vehicle_make']} {vehicle['vehicle_model']}."}
        ]
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '{}')
        parsed = json.loads(content)
    except Exception as e:
        logging.error("Error processing OpenAI response", exc_info=True)
        parsed = {}

    defaults = {
        "technical_explanation": "Not available.",
        "layman_explanation": "Not available.",
        "urgency_percent": 0,
        "urgency_label": "Unknown",
        "repair_cost_cad": "N/A",
        "consequences": "N/A",
        "preventative_tips": [],
        "diy_potential": "N/A",
        "environmental_impact": 0,
        "video_explanation_url": "#",
        "video_diy_url": "#",
        "video_consequences_url": "#",
        "mechanics": []
    }
    for key, fallback in defaults.items():
        if key not in parsed or parsed[key] in [None, "", []]:
            parsed[key] = fallback

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    return render_template(
        "report.html",
        **customer,
        **vehicle,
        technical_explanation=parsed["technical_explanation"],
        layman_explanation=parsed["layman_explanation"],
        urgency_percent=parsed["urgency_percent"],
        urgency_label=parsed["urgency_label"],
        repair_cost_cad=parsed["repair_cost_cad"],
        consequences=parsed["consequences"],
        preventative_tips=parsed["preventative_tips"],
        diy_potential=parsed["diy_potential"],
        environmental_impact=parsed["environmental_impact"],
        video_explanation_url=clean_url(parsed["video_explanation_url"]),
        video_diy_url=clean_url(parsed["video_diy_url"]),
        video_consequences_url=clean_url(parsed["video_consequences_url"]),
        mechanics=parsed["mechanics"],
        timestamp=timestamp
    )

if __name__ == "__main__":
    app.run(debug=True)
