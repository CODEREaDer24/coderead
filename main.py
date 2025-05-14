from flask import Flask, render_template, request
import logging
import requests
import json
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def validate_url(url: str) -> bool:
    return url.startswith('https://') and not url.rstrip().endswith('.')

@app.route('/report', methods=['POST'])
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
            {"role": "system", "content": "Return valid JSON with: technical_explanation, layman_explanation, urgency_percent, urgency_label, repair_cost_cad, consequences, preventative_tips (list), diy_potential, environmental_impact, video_explanation_url, video_diy_url, video_consequences_url, mechanics (list of {name,rating,phone})"},
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

    # Sanitize fields
    tech = parsed.get('technical_explanation', 'N/A')
    lay = parsed.get('layman_explanation', 'N/A')
    urgency = int(parsed.get('urgency_percent', 0))
    label = parsed.get('urgency_label', 'Unknown')
    cost = parsed.get('repair_cost_cad', 'N/A')
    cons = parsed.get('consequences', 'N/A')
    tips = parsed.get('preventative_tips', [])
    diy = parsed.get('diy_potential', 'N/A')
    env = int(parsed.get('environmental_impact', 0))

    # Video links
    video_explanation_url = parsed.get('video_explanation_url', '#')
    video_diy_url = parsed.get('video_diy_url', '#')
    video_consequences_url = parsed.get('video_consequences_url', '#')
    for v in [video_explanation_url, video_diy_url, video_consequences_url]:
        if not validate_url(v): v = '#'

    mechanics = parsed.get('mechanics', [])
    if not isinstance(mechanics, list):
        mechanics = []

    return render_template(
        'report.html',
        **customer,
        **vehicle,
        technical_explanation=tech,
        layman_explanation=lay,
        urgency_percent=urgency,
        urgency_label=label,
        repair_cost_cad=cost,
        consequences=cons,
        preventative_tips=tips,
        diy_potential=diy,
        environmental_impact=env,
        video_explanation_url=video_explanation_url,
        video_diy_url=video_diy_url,
        video_consequences_url=video_consequences_url,
        mechanics=mechanics
    )

if __name__ == '__main__':
    app.run(debug=True) 
