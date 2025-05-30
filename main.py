from flask import Flask, render_template, request
import openai
import os
import re

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/report', methods=['POST'])
def report():
    name = request.form.get('name', 'Unknown')
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    make = request.form.get('make', 'Unknown')
    model = request.form.get('model', 'Unknown')
    year = request.form.get('year', 'Unknown')
    codes = request.form.get('codes', '')

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are CodeREAD AI, an expert automotive diagnostic assistant."},
                {"role": "user", "content": f"""Analyze the following OBD-II codes: {codes}.
Respond with the following in plain text (no formatting, just label and value):

LAYMAN_EXPLANATION:
TECHNICAL_EXPLANATION:
URGENCY_LEVEL:
REPAIR_COST:
CONSEQUENCES:
PREVENTATIVE_TIPS:
DIY_POTENTIAL:
ENVIRONMENTAL_IMPACT:
AI_RECOMMENDATION:
VIDEO_EXPLAINER:
VIDEO_DIY:
"""}
            ]
        )

        parsed = response['choices'][0]['message']['content']
        print("\n--- RAW AI OUTPUT ---\n", parsed)

        def extract(tag):
            match = re.search(rf"{tag}:\s*(.+?)(?=\n[A-Z_]+:|\Z)", parsed, re.DOTALL)
            return match.group(1).strip() if match else "Data not available"

        urgency_raw = extract("URGENCY_LEVEL")
        urgency = int(urgency_raw) if urgency_raw.isdigit() else 5
        urgency_percent = min(max((urgency / 10) * 100, 0), 100)
        urgency_label = "Immediate – See Mechanic" if urgency > 7 else "Fine for Now" if urgency <= 3 else "Can Wait Until Next Visit"

        return render_template('report.html',
            name=name,
            phone=phone,
            email=email,
            make=make,
            model=model,
            year=year,
            codes=codes,
            urgency_level=urgency,
            urgency_percent=urgency_percent,
            urgency_label=urgency_label,
            layman_explanation=extract("LAYMAN_EXPLANATION"),
            technical_explanation=extract("TECHNICAL_EXPLANATION"),
            repair_cost=extract("REPAIR_COST"),
            consequences=extract("CONSEQUENCES"),
            preventative_tips=extract("PREVENTATIVE_TIPS"),
            diy_potential=extract("DIY_POTENTIAL"),
            environmental_impact=extract("ENVIRONMENTAL_IMPACT"),
            ai_recommendation=extract("AI_RECOMMENDATION"),
            video_explainer=extract("VIDEO_EXPLAINER"),
            video_diy=extract("VIDEO_DIY")
        )

    except Exception as e:
        print("Error generating report:", str(e))
        return render_template('report.html',
            name=name,
            phone=phone,
            email=email,
            make=make,
            model=model,
            year=year,
            codes=codes,
            urgency_level=5,
            urgency_percent=50,
            urgency_label="Unknown",
            layman_explanation="Could not generate explanation.",
            technical_explanation="N/A",
            repair_cost="Unavailable",
            consequences="Unknown",
            preventative_tips="Unknown",
            diy_potential="Unknown",
            environmental_impact="Unknown",
            ai_recommendation="Unable to generate recommendation.",
            video_explainer="https://youtube.com",
            video_diy="https://youtube.com"
        )

if __name__ == '__main__':
    app.run(debug=True)
