from flask import Flask, render_template, request
import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY is missing. Check your environment variables.")

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
    You are CodeREAD, an expert automotive AI trained to analyze vehicle OBD2 codes.
    The user submitted the code {code} for vehicle {vehicle}.

    Return a detailed diagnostic report covering the following 9 sections:

    1. Technical Summary (what the code means)
    2. Layman Summary (plain English)
    3. Urgency Rating (1–10) and explanation
    4. Estimated Repair Cost in CAD
    5. Consequences of Not Fixing
    6. Preventative Maintenance Tips
    7. DIY Potential
    8. Environmental Impact
    9. Related YouTube Video link (real link only)

    Format your response exactly like this, using a double-pipe (||) to separate sections, all on one line:

    [Technical Summary] || [Layman Summary] || [Urgency Rating and explanation] || [Repair Cost] || [Consequences] || [Preventative Tips] || [DIY Potential] || [Environmental Impact] || [YouTube Link]
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )

        result = response.choices[0].message['content']
        parts = result.split('||')
        if len(parts) < 9:
            raise ValueError("Incomplete GPT response")

        urgency_text = parts[2].strip()
        urgency_num = ''.join(filter(str.isdigit, urgency_text)) or "5"
        urgency_position = min(int(urgency_num), 10) * 10

        return render_template("report.html",
            name=name,
            email=email,
            vehicle=vehicle,
            code=code,
            tech_summary=parts[0].strip(),
            layman_summary=parts[1].strip(),
            urgency=urgency_num,
            urgency_explanation=urgency_text,
            urgency_position=urgency_position,
            repair_cost=parts[3].strip(),
            consequences=parts[4].strip(),
            preventative_tips=parts[5].strip(),
            diy_potential=parts[6].strip(),
            environmental_impact=parts[7].strip(),
            video_link=parts[8].strip(),
            recommended_mechanic="Clover Auto & Tecumseh Auto (Windsor)"
        )

    except Exception as e:
        return f"AI report generation failed: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
