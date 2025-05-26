from flask import Flask, render_template, request
import openai
import os

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
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    make = request.form['make']
    model = request.form['model']
    year = request.form['year']
    codes = request.form['codes']

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are CodeREAD AI, an expert automotive diagnostic assistant."},
            {"role": "user", "content": f"""Analyze the following OBD-II codes: {codes}.
Respond with the following:
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
    def extract(tag): return parsed.split(f"{tag}:")[1].split("\n", 1)[0].strip() if f"{tag}:" in parsed else ""

    urgency = int(extract("URGENCY_LEVEL")) if extract("URGENCY_LEVEL").isdigit() else 5
    urgency_percent = min(max((urgency / 10) * 100, 0), 100)
    urgency_label = "Immediate – See Mechanic" if urgency > 7 else "Fine for Now" if urgency <= 3 else "Can Wait Until Next Visit"

    return render_template('report.html',
        name=name, phone=phone, email=email, make=make, model=model, year=year, codes=codes,
        layman_explanation=extract("LAYMAN_EXPLANATION"),
        technical_explanation=extract("TECHNICAL_EXPLANATION"),
        urgency_level=urgency,
        urgency_percent=urgency_percent,
        urgency_label=urgency_label,
        repair_cost=extract("REPAIR_COST"),
        consequences=extract("CONSEQUENCES"),
        preventative_tips=extract("PREVENTATIVE_TIPS"),
        diy_potential=extract("DIY_POTENTIAL"),
        environmental_impact=extract("ENVIRONMENTAL_IMPACT"),
        ai_recommendation=extract("AI_RECOMMENDATION"),
        video_explainer=extract("VIDEO_EXPLAINER"),
        video_diy=extract("VIDEO_DIY")
    )

if __name__ == '__main__':
    app.run(debug=True)
