from flask import Flask, render_template, request
import os

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

    urgency = "6"
    urgency_position = int(urgency) * 10
    urgency_explanation = "Moderate concern – emissions system not warming up efficiently."
    tech_summary = f"The {code} code is triggered by poor performance in the catalytic converter heater circuit."
    layman_summary = "Your emissions system isn’t warming up fast enough, which can fail tests and harm the engine over time."
    repair_cost = "Estimate: $600–$2,000 CAD depending on parts and labour."
    consequences = "Vehicle may fail emissions testing. Long-term engine damage if ignored."
    preventative_tips = "Drive longer trips occasionally to help the system reach operating temp. Regular checkups help."
    diy_potential = "Low. Diagnosis and fix often require a mechanic with proper tools."
    environmental_impact = "Increased emissions and lower fuel efficiency."
    recommended_mechanic = "Clover Auto & Tecumseh Auto (Windsor)."
    video_link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    return render_template("report.html",
        name=name,
        vehicle=vehicle,
        code=code,
        email=email,
        urgency=urgency,
        urgency_position=urgency_position,
        urgency_explanation=urgency_explanation,
        tech_summary=tech_summary,
        layman_summary=layman_summary,
        repair_cost=repair_cost,
        consequences=consequences,
        preventative_tips=preventative_tips,
        diy_potential=diy_potential,
        environmental_impact=environmental_impact,
        recommended_mechanic=recommended_mechanic,
        video_link=video_link
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
