from flask import Flask, render_template, request, send_file
import pdfkit
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/generate_report', methods=['POST'])
def generate_report():
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    vehicle = request.form.get('vehicle')
    codes = request.form.get('codes')

    code_list = [c.strip().upper() for c in codes.split(',') if c.strip()]
    urgency = calculate_urgency(code_list)

    rendered = render_template(
        'report.html',
        name=name,
        phone=phone,
        email=email,
        vehicle=vehicle,
        codes=code_list,
        urgency=urgency
    )

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f'coderead_report_{timestamp}.pdf'
    filepath = os.path.join('static', filename)
    
    pdfkit.from_string(rendered, filepath)

    return rendered  # Show HTML. Optionally: `send_file(filepath)` for download

def calculate_urgency(codes):
    if not codes:
        return 0
    score = 0
    for code in codes:
        if code.startswith("P0"):  # Generic powertrain
            score += 15
        elif code.startswith("P2"):  # Manufacturer specific
            score += 10
        else:
            score += 5
    return min(score, 100)

if __name__ == '__main__':
    app.run(debug=True)
