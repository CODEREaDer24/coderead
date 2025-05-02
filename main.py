from flask import Flask, request, render_template, send_file
import os
import openai
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate-report", methods=["POST"])
def generate_report():
    name = request.form.get("name")
    vehicle = request.form.get("vehicle")
    code = request.form.get("code")
    email = request.form.get("email")

    analysis = get_code_analysis(code)
    pdf = generate_pdf(name, vehicle, code, email, analysis)
    send_report_email(email, pdf, name, code)

    pdf.seek(0)
    return send_file(pdf, as_attachment=True, download_name="CodeREAD_Report.pdf", mimetype="application/pdf")

def get_code_analysis(code):
    try:
        prompt = (
            f"You're CodeREAD, a car diagnostic assistant. Explain OBD2 code {code} including:\n"
            "- Simple description\n"
            "- Urgency scale 1–10\n"
            "- Consequences of ignoring it\n"
            "- Repair options (pro & DIY)\n"
            "- Environmental impact"
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"Error generating analysis: {e}"

def generate_pdf(name, vehicle, code, email, analysis):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    text = p.beginText(50, 750)
    text.setFont("Helvetica", 12)

    lines = [
        "CodeREAD Vehicle Diagnostic Report",
        "----------------------------------",
        f"Customer Name: {name}",
        f"Vehicle: {vehicle}",
        f"OBD2 Code: {code}",
        f"Email: {email}",
        "",
        "AI Diagnostic Analysis:",
    ] + analysis.split('\n')

    for line in lines:
        text.textLine(line.strip())

    p.drawText(text)
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def send_report_email(to_email, pdf_buffer, name, code):
    try:
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")

        msg = EmailMessage()
        msg["Subject"] = f"CodeREAD Report for {name} – Code {code}"
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg.set_content(f"Hi {name},\n\nAttached is your diagnostic report for code {code}.\n\n- CodeREAD")

        pdf_buffer.seek(0)
        msg.add_attachment(pdf_buffer.read(), maintype="application", subtype="pdf", filename="CodeREAD_Report.pdf")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    except Exception as e:
        print(f"Email error: {e}")
