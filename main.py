from flask import Flask, render_template, request
from flask_mail import Mail, Message
from xhtml2pdf import pisa
from io import BytesIO
import os

app = Flask(__name__)

# Load email config from environment or .env
app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/generate', methods=['POST'])
def generate():
    name = request.form.get('name')
    email = request.form.get('email')
    vehicle = request.form.get('vehicle')
    code = request.form.get('code').upper()

    urgency = "6"
    urgency_explanation = "Moderate concern – emissions system not warming up efficiently."
    tech_summary = f"The {code} code is triggered by poor performance in the catalytic converter heater circuit."
    layman_summary = "Your emissions system isn’t warming up fast enough, which can fail tests and harm the engine over time."
    repair_cost = "Estimate: $600–$2,000 CAD"
    consequences = "Vehicle may fail emissions testing."
    preventative_tips = "Drive longer trips occasionally."
    diy_potential = "Low"
    environmental_impact = "Increased emissions."
    recommended_mechanic = "Clover Auto & Tecumseh Auto (Windsor)"
    video_link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    rendered = render_template("report.html",
        name=name, vehicle=vehicle, code=code, email=email,
        urgency=urgency, urgency_explanation=urgency_explanation,
        tech_summary=tech_summary, layman_summary=layman_summary,
        repair_cost=repair_cost, consequences=consequences,
        preventative_tips=preventative_tips, diy_potential=diy_potential,
        environmental_impact=environmental_impact, recommended_mechanic=recommended_mechanic,
        video_link=video_link
    )

    # Generate PDF
    pdf = BytesIO()
    pisa.CreatePDF(rendered, dest=pdf)
    pdf.seek(0)

    # Send email with PDF
    msg = Message("Your CodeREAD Diagnostic Report", recipients=[email])
    msg.body = "Attached is your diagnostic report from CodeREAD."
    msg.attach("CodeREAD_Report.pdf", "application/pdf", pdf.read())
    mail.send(msg)

    return rendered

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
