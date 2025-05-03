from flask import Flask, render_template, request, send_file
from flask_mail import Mail, Message
from openai import OpenAI
from dotenv import load_dotenv
from xhtml2pdf import pisa
import os
import io

load_dotenv()

app = Flask(__name__)

# Config from .env
app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/report', methods=['POST'])
def generate_report():
    name = request.form['name']
    email = request.form['email']
    code = request.form['code']
    vehicle = f"{request.form['year']} {request.form['make']} {request.form['model']}"

    # Ask OpenAI for analysis
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": f"Explain OBD2 code {code} in detail. Include cost, urgency (1–10), consequences, DIY options, and environmental impact."
        }]
    )
    analysis = response.choices[0].message.content.strip()

    # Make HTML for PDF
    html = render_template('report_template.html', name=name, email=email, vehicle=vehicle, code=code, analysis=analysis)

    # Convert HTML to PDF
    pdf_stream = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html), dest=pdf_stream)
    pdf_stream.seek(0)

    # Send email
    msg = Message(subject="Your CodeRead Report",
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[email])
    msg.body = f"Hi {name},\n\nYour vehicle diagnostic report is attached.\n\n- CodeRead"
    msg.attach("report.pdf", "application/pdf", pdf_stream.read())
    mail.send(msg)

    return f"Report sent to {email}!"

if __name__ == '__main__':
    app.run(debug=True)
