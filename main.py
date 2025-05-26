from flask import Flask, render_template, request
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_code(codes):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are CodeREAD AI, an expert automotive diagnostic analyst."},
            {"role": "user", "content": f"""Analyze the following OBD-II codes: {codes}.
Please provide:
1. Layman’s Explanation
2. Technical Explanation
3. Urgency Level (1-10)
4. Estimated Repair Cost in CAD
5. Consequences of Ignoring
6. Preventative Care Tips
7. DIY Repair Potential
8. Environmental Impact
9. AI Recommendation tailored to DIYer or non-DIYer
10. YouTube video links: (a) code explanation, (b) DIY repair

Respond in this exact format:
LAYMAN_EXPLANATION:
...
TECHNICAL_EXPLANATION:
...
URGENCY_LEVEL:
...
REPAIR_COST:
...
CONSEQUENCES:
...
PREVENTATIVE_TIPS:
...
DIY_POTENTIAL:
...
ENVIRONMENTAL_IMPACT:
...
AI_RECOMMENDATION:
...
VIDEO_EXPLAINER:
...
VIDEO_DIY:
...
"""}
        ]
    )
    return response['choices'][0]['message']['content']

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/report', methods=['POST'])
def report():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    make = request.form['make']
    model = request.form['model']
    year = request.form['year']
    codes = request.form['codes']

    parsed = analyze_code(codes)

    fields = {
        'LAYMAN_EXPLANATION': '',
        'TECHNICAL_EXPLANATION': '',
        'URGENCY_LEVEL': '',
        'REPAIR_COST': '',
        'CONSEQUENCES': '',
        'PREVENTATIVE_TIPS': '',
        'DIY_POTENTIAL': '',
        'ENVIRONMENTAL_IMPACT': '',
        'AI_RECOMMENDATION': '',
        'VIDEO_EXPLAINER': '',
        'VIDEO_DIY': ''
    }

    for key in fields:
        tag = key + ":"
        if tag in parsed:
            start = parsed.index(tag) + len(tag)
            end = next((parsed.index(k + ":", start) for k in fields if k + ":" in parsed[start:]), len(parsed))
            fields[key] = parsed[start:end].strip()

    urgency = int(fields['URGENCY_LEVEL']) if fields['URGENCY_LEVEL'].isdigit() else 5
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
        layman_explanation=fields['LAYMAN_EXPLANATION'],
        technical_explanation=fields['TECHNICAL_EXPLANATION'],
        urgency_level=urgency,
        urgency_percent=urgency_percent,
        urgency_label=urgency_label,
        repair_cost=fields['REPAIR_COST'],
        consequences=fields['CONSEQUENCES'],
        preventative_tips=fields['PREVENTATIVE_TIPS'],
        diy_potential=fields['DIY_POTENTIAL'],
        environmental_impact=fields['ENVIRONMENTAL_IMPACT'],
        ai_recommendation=fields['AI_RECOMMENDATION'],
        video_explainer=fields['VIDEO_EXPLAINER'],
        video_diy=fields['VIDEO_DIY']
    )

if __name__ == '__main__':
    app.run(debug=True)
