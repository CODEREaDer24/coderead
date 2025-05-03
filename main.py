from flask import Flask, render_template, request
import os

app = Flask(__name__)

# Homepage route – serves the diagnostic form
@app.route('/')
def index():
    return render_template('form.html')

# Generate route – builds the report from submitted form data
@app.route('/generate', methods=['POST'])
def generate():
    name = request.form.get('name', 'Unknown')
    email = request.form.get('email', 'unknown@example.com')
    vehicle = request.form.get('vehicle', 'Unknown Vehicle')
    code = request.form.get('code', 'N/A').upper()

    # === Placeholder logic until OpenAI is integrated ===
    urgency = "6"
    urgency_explanation = "Moderate concern – emissions system not warming up efficiently."
    tech_summary = f"The diagnostic trouble code {code} indicates a potential issue in the emission system, likely related to catalytic converter efficiency or sensor feedback."
    layman_summary = "This code means your car isn't processing emissions correctly. It might fail a test or run rough if ignored."
    repair_cost = "Estimated repair: $600–$2,000 CAD depending on diagnosis and parts."
    consequences = "Ignoring this could result in poor fuel economy, failed emissions, or damage to the engine."
    preventative_tips = "Schedule regular maintenance and emissions checks. Avoid excessive idling and short trips."
    diy_potential = "Low to Moderate – may require scan tools and mechanical skill."
    environmental_impact = "Elevated emissions, reduced fuel efficiency, higher pollution."
    recommended_mechanic = "Clover Auto & Tecumseh Auto – Trusted in Windsor."
    video_link = f"https://www.youtube.com/results?search_query=OBD2+Code+{code}+explanation"

    return render_template("report.html",
        name=name,
        vehicle=vehicle,
        code=code,
        email=email,
        urgency=urgency,
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

# Required for deployment on Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
