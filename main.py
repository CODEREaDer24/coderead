from flask import Flask, render_template, request
import os
import openai
from dotenv import load_dotenv

load_dotenv()
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
    You are CodeREAD, an AI car diagnostics expert.
    The user submitted OBD2 trouble code {code}.

    Generate a diagnostic report with the following sections, separated by "|":
    1. Technical Summary
    2. Layman's Summary
    3. Urgency (1–10)
    4. Urgency Explanation
    5. Estimated Repair Cost (CAD)
    6. Consequences of Ignoring
    7. Preventative Maintenance Tips
    8. DIY Potential
    9. Environmental Impact

    Write all responses clearly and in plain text. No formatting or markdown.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        parts = response.choices[0].message["content"].split('|')
        if len(parts) < 9:
            raise ValueError("Incomplete response from OpenAI.")

        urgency = parts[2].strip()
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
