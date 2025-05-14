from flask import Flask, render_template, request
import logging
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def validate_url(url):
    return url.startswith('https://') and not url.rstrip().endswith('.')

@app.route('/report', methods=['POST'])
def report():
    data = request.form.to_dict()
    # Map inputs
    customer = {
      'customer_name': data.get('name', 'N/A'),
      'customer_email': data.get('email', 'N/A'),
      'customer_phone': data.get('phone', 'N/A')
    }
    vehicle = {
      'vehicle_make': data.get('make', '').capitalize(),
      'vehicle_model': data.get('model', '').upper(),
      'vehicle_year': data.get('year', ''),
      'code': data.get('code', '')
    }

    # Call AI API (pseudo)
    ai_response = requests.post('https://api.openai.com/v1/…', json={'code': vehicle['code']})
    content = ai_response.json()

    # Pull AI fields safely
    tech = content.get('technical_explanation', 'No data')
    lay = content.get('layman_explanation', 'No data')
    urgency = int(content.get('urgency_percent', 0))
    label = content.get('urgency_label', '')
    cost = content.get('repair_cost_cad', '0')
    cons = content.get('consequences', 'None specified')
    tips = content.get('preventative_tips', [])
    diy = content.get('diy_potential', 'Not recommended')
    env = int(content.get('environmental_impact', 0))

    # Video URLs with validation
    videos = {
      'video_explanation_url': content.get('video_explanation_url', ''),
      'video_diy_url': content.get('video_diy_url', ''),
      'video_consequences_url': content.get('video_consequences_url', '')
    }
    for k, url in videos.items():
      if not validate_url(url):
        logging.warning(f'Invalid URL for {k}: {url}')
        videos[k] = '#'

    # Mechanics list (ensure safety)
    raw_mechs = content.get('mechanics', [])
    mechanics = []
    for m in raw_mechs:
      if all(m.get(k) for k in ('name','rating','phone')):
        mechanics.append(m)

    return render_template('report.html',
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
    app.run(debug=True)
