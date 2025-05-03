import os
from flask import Flask, render_template, request, send_file
from dotenv import load_dotenv
import openai
from fpdf import FPDF
import smtplib
from email.message import EmailMessage

# Load environment variables from .env
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Email credentials
EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

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

    prompt = f"""Provide a full vehicle diagnostic summary for OBD2 code {code}.
    Include:
    1. Technical explanation
    2. Layman’s explanation
    3. Urgency (1–10)
    4. Repair cost estimate in CAD
    5. Consequences if not fixed
    6. Preventative tips
    7. DIY potential
    8. Environmental impact
    9. Recommended mechanic in Windsor, Ontario
    10. Link to YouTube video explaining the code"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        output = response['choices'][0]['message']['content']
    except Exception as e:
        return f"AI report generation failed: {e}"

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"CodeREAD Diagnostic Report\n\nCustomer: {name}\nVehicle: {vehicle}\nCode: {code}\n\n{output}")

    pdf_file_path = "/tmp/report.pdf"
    pdf.output(pdf_file_path)

    # Email PDF
    msg = EmailMessage()
    msg['Subject'] = f'Your CodeREAD Report for {code}'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg.set_content("Attached is your detailed CodeREAD diagnostic report.")

    with open(pdf_file_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename='CodeREAD_Report.pdf')

    try:
        with smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        return f"Email sending failed: {e}"

    return send_file(pdf_file_path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
