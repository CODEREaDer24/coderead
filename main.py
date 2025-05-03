from flask import Flask, render_template, request
import os
import openai
from dotenv import load_dotenv

# Load environment variables from a .env file (if running locally)
load_dotenv()

# Ensure the API key is correctly set from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/generate', methods=['POST'])
def generate():
    name = request.form.get('name', 'Unknown')
    email = request.form.get('email', 'unknown@example.com')
    vehicle = request.form.get('vehicle', 'Unknown Vehicle')
    code = request.form.get('code', 'N/A').upper()

    prompt = f"""
    You are CodeREAD, an AI automotive diagnostic expert.

    A customer has submitted OBD2 code: {code}

    Please return your response using this **strict format** with sections separated by "|" on a single line:

    [1] Technical Summary |
    [2] Layman's Summary |
    [3] Urgency (1–10 as a number only) |
    [4] Urgency Explanation |
    [5] Repair Cost Estimate in CAD |
    [6] Consequences of Ignoring |
    [7] Preventative Maintenance Tips |
    [8] DIY Potential |
    [9] Environmental Impact

    Do not add commentary, labels, or line breaks. Keep it on a single line.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        parts = response.choices[0].message["content"].split('|')
        if len(parts) < 9:
            raise ValueError("Incomplete GPT response")

        # Safely parse urgency as int
        urgency_raw = parts[2].strip()
        urgency = ''.join(filter(str.isdigit, urgency_raw)) or "5"
        urgency_position = min(int(urgency), 10) * 10

        return render_template("report.html",
            name=name,
            email=email,
            vehicle=vehicle,
            code=code,
            urgency=urgency,
            urgency_position=urgency_position,
            urgency_explanation=parts[3].strip(),
            tech_summary=parts[0].strip(),
            layman_summary=parts[1].strip(),
            repair_cost=parts[4].strip(),
            consequences=parts[5].strip(),
            preventative_tips=parts[6].strip(),
            diy_potential=parts[7].strip(),
            environmental_impact=parts[8].strip(),
            recommended_mechanic="Clover Auto & Tecumseh Auto (Windsor)",
            video_link="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )

    except Exception as e:
        return f"AI report generation failed: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
