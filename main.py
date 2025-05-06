from flask import Flask, request, render_template, send_file
from openai import OpenAI
from fpdf import FPDF
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
from code_analyzer import analyze_codes  # <- You must create this module based on our structure

load_dotenv()

app = Flask(__name__)

openai_api_key = os.getenv("OPENAI_API_KEY")
email_sender = os.getenv("EMAIL_SENDER")
email_password = os.getenv("EMAIL_PASSWORD")

@app.route("/")
def home():
    return render_template("report.html")

@app.route("/generate_report", methods=["POST"])
def generate_report():
    data = {
        "customer_name": request.form["customer_name"],
        "address": request.form["address"],
        "phone": request.form["phone"],
        "email": request.form["email"],
        "make": request.form["make"],
        "model": request.form["model"],
        "year": request.form["year"],
        "codes": request.form["codes"]
    }

    code_list = [code.strip().upper() for code in data["codes"].split(",")]
    analysis = analyze_codes(code_list, data)

    pdf_path = create_pdf_report(data, analysis)
    send_email_with_pdf(data["email"], pdf_path)

    return send_file(pdf_path, as_attachment=True)

def create_pdf_report(data, analysis):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "CodeREAD Diagnostic Report", ln=True, align="C")
    pdf.ln(10)

    # Customer Info
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Customer: {data['customer_name']}\nAddress: {data['address']}\nPhone: {data['phone']}\nEmail: {data['email']}\nVehicle: {data['year']} {data['make']} {data['model']}\n")
    pdf.ln(5)

    for item in analysis:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Code: {item['code']}", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"Issue: {item['issue']}\nPlain Language: {item['layman']}\nUrgency (1–10): {item['urgency']}\nRepair Cost: {item['cost']} CAD\nConsequences: {item['consequences']}\nPreventative Tips: {item['preventative']}\nDIY Potential: {item['diy']}\nEnvironmental Impact: {item['environment']}\nInterrelationships: {item['interrelationships']}\n")
        pdf.multi_cell(0, 10, f"Video Explanation: {item['video_link']}\nDIY Guide: {item['diy_video']}\nParts: {item['parts_link']}\nRecommended Mechanics: {item['mechanics']}")
        pdf.ln(10)

    filename = f"/tmp/report_{data['customer_name'].replace(' ', '_')}.pdf"
    pdf.output(filename)
    return filename

def send_email_with_pdf(to_email, file_path):
    msg = MIMEMultipart()
    msg["From"] = email_sender
    msg["To"] = to_email
    msg["Subject"] = "Your CodeREAD Diagnostic Report"

    body = "Attached is your full diagnostic report from CodeREAD.ca.\nVisit www.read.codes for more info."
    msg.attach(MIMEText(body, "plain"))

    with open(file_path, "rb") as f:
        part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(file_path)}"'
        msg.attach(part)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email_sender, email_password)
    server.send_message(msg)
    server.quit()

if __name__ == "__main__":
    app.run(debug=True)
