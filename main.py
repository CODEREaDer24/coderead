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
    name = request.form.get('name')
    email = request.form.get('email')
    vehicle = request.form.get('vehicle')
    code = request.form.get('code')

    prompt = f"""
You are CodeREAD, an expert automotive AI trained to analyze vehicle OBD2 codes. The user submitted the code {code} for vehicle {vehicle}.
Return a diagnostic report with 10 full sections, separated by double pipes (||), in this order:
1. Technical Summary
2. Layman Summary
3. Urgency rating (1–10) + short explanation
4. Estimated Repair Cost in CAD
5. Consequences of Not Fixing
6. Preventative Maintenance Tips
7. DIY Potential with link to a real DIY video
8. Environmental Impact
9. Parts Needed (with link to a real part on Amazon or RockAuto)
10. Mechanic Recommendations for Windsor with Google Map links

Strict format:
[Technical Summary] || [Layman Summary] || [Urgency Rating and explanation] || [Repair Cost] || [Consequences] || [Preventative Tips] || [DIY Potential and Video] || [Environmental Impact] || [Parts Recommendation with Link] || [Mechanic List with Links]
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        result = response.choices[0].message['content']
        parts = [part.strip() for part in result.split("||")]

        if len(parts) < 10:
            raise ValueError("Incomplete response from GPT.")

        urgency_text = parts[2]
        urgency_num = ''.join(filter(str.isdigit, urgency_text)) or "5"
        urgency_position = min(int(urgency_num), 10) * 10

        return render_template("report.html",
            name=name,
            email=email,
            vehicle=vehicle,
            code=code,
            tech_summary=parts[0],
            layman_summary=parts[1],
            urgency=urgency_num,
            urgency_explanation=urgency_text,
            urgency_position=urgency_position,
            repair_cost=parts[3],
            consequences=parts[4],
            preventative_tips=parts[5],
            diy_potential=parts[6],
            environmental_impact=parts[7],
            parts_recommendation=parts[8],
            mechanic_list=parts[9],
            video_links=parts[6]  # Assuming DIY video is in section 7
        )
    except Exception as e:
        return f"AI report generation failed: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
