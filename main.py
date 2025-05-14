#!/usr/bin/env python3
from flask import Flask, render_template, request
import logging
import requests
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def validate_url(url: str) -> bool:
    return url.startswith('https://') and not url.rstrip().endswith('.')

@app.route('/report', methods=['POST'])
def report():
    # 1. Collect form data
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

    # 2. Call AI API for analysis
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
      "model": "gpt-4o-mini",
      "messages": [
        {"role": "system", "content": "Generate JSON with fields: technical_explanation, layman_explanation, urgency_percent, urgency_label, repair_cost_cad, consequences, preventative_tips (list), diy_potential, environmental_impact, video_explanation_url, video_diy_url, video_consequences_url, mechanics (list of {name,rating,phone})."},
        {"role": "user", "content": f"Analyze OBD2 code {vehicle['code']} for a {vehicle['vehicle_year']} {vehicle['vehicle_make']} {vehicle['vehicle_model']}."}
      ]
    }
    resp = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=payload)
    content = resp.json().get('choices', [{}])[0].get('message', {}).get('content', '{}')
    try:
        analysis = json.loads(content)
    except Exception:
        logging.error("Failed to parse AI response JSON", exc_info=True)
        analysis = {}

    # 3. Extract and sanitize
    tech = analysis.get('technical_explanation', 'No data')
    lay = analysis.get('layman_explanation', 'No data')
    urgency = int(analysis.get('urgency_percent', 0))
    label = analysis.get('urgency_label', 'Unknown')
    cost = analysis.get('repair_cost_cad', '0')
    cons = analysis.get('consequences', 'None specified')
    tips = analysis.get('preventative_tips', [])
    diy = analysis.get('diy_potential', 'Not recommended')
    env = int(analysis.get('environmental_impact', 0))

    # 4. Validate video URLs
    videos = {
        'video_explanation_url': analysis.get('video_explanation_url', ''),
        'video_diy_url': analysis.get('video_diy_url', ''),
        'video_consequences_url': analysis.get('video_consequences_url', '')
    }
    for k, url in videos.items():
        if not validate_url(url):
            logging.warning(f'Invalid URL for {k}: {url}')
            videos[k] = '#'

    # 5. Clean mechanics list
    mechanics = []
    for m in analysis.get('mechanics', []):
        if all(m.get(field) for field in ('name','rating','phone')):
            mechanics.append(m)

    # 6. Render
    return render_template(
        'report.html',
        **customer, **vehicle,
        technical_explanation=tech,
        layman_explanation=lay,
        urgency_percent=urgency,
        urgency_label=label,
        repair_cost_cad=cost,
        consequences=cons,
        preventative_tips=tips,
        diy_potential=diy,
        environmental_impact=env,
        mechanics=mechanics,
        **videos
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
