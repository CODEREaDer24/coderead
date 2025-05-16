import os
import logging
from flask import Flask, render_template, request
import openai

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Setup logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/report', methods=['POST'])
def report():
    try:
        # Collect form data
        customer_name = request.form.get('name', '')
        vehicle_make = request.form.get('make', '')
        vehicle_model = request.form.get('model', '')
        vehicle_year = request.form.get('year', '')
        diagnostic_code = request.form.get('code', '')

        # Build prompt for GPT
        prompt = f"""
You are CodeREAD, an AI automotive diagnostics assistant. A customer has submitted a check engine code and vehicle details. Provide a detailed diagnostic report including:

- Diagnostic code: {diagnostic_code}
- Vehicle: {vehicle_year} {vehicle_make} {vehicle_model}
- Explanation (technical + layman)
- Urgency (1–10)
- Estimated repair cost (CAD)
- Consequences of not fixing it
- Preventative tips
- DIY potential
- Environmental impact
- AI recommendation (based on if the user is DIY or not)

Only include accurate and complete information.

Customer Name: {customer_name}
"""

        # Call OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            timeout=20
        )

        gpt_output = response['choices'][0]['message']['content'].strip()

        if not gpt_output:
            raise ValueError("GPT returned empty content")

        return render_template('report.html', report=gpt_output, error=None)

    except Exception as e:
        logging.error("GPT API error: %s", str(e))
        return render_template('report.html', report=None, error="Our AI failed to generate a valid report. Please try again soon.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
