from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import sqlite3
import os
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
DATABASE = 'coderead.db'

MECHANICS = [
    {"name": "DLH Auto Service", "address": "2378 Central Ave, Windsor, ON N8W 4J2", "maps": "https://maps.google.com/?q=2378+Central+Ave+Windsor+ON"},
    {"name": "Demario’s Auto Clinic", "address": "2366 Dougall Ave, Windsor, ON N8X 1T1", "maps": "https://maps.google.com/?q=2366+Dougall+Ave+Windsor+ON"},
    {"name": "Kipping Tire & Automotive", "address": "1197 Ouellette Ave, Windsor, ON N9A 4K1", "maps": "https://maps.google.com/?q=1197+Ouellette+Ave+Windsor+ON"},
]

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 email TEXT,
                 code TEXT,
                 phone TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    code = request.form['code'].upper().strip()
    phone = request.form.get('phone', '')

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO reports (name, email, code, phone) VALUES (?, ?, ?, ?)", (name, email, code, phone))
    conn.commit()
    conn.close()

    advice, urgency = analyze_code(code)
    pdf_path = create_pdf(name, email, code, phone, advice, urgency)

    if email:
        send_email(email, pdf_path)

    return render_template('report.html', name=name, code=code, advice=advice, urgency=urgency, pdf_path=pdf_path, mechanics=MECHANICS)

def analyze_code(code):
    severity_scale = {
        "P0300": ("Random/Multiple Misfire Detected", 90),
        "P0420": ("Catalyst System Efficiency Below Threshold", 60),
        "P0171": ("System Too Lean (Bank 1)", 70),
        "P0455": ("Evaporative Emission System Leak Detected", 50),
    }
    return severity_scale.get(code, ("Code not recognized. Further diagnosis needed.", 40))

def create_pdf(name, email, code, phone, advice, urgency):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(255, 0, 0)
    pdf.cell(200, 10, "CodeREAD Diagnostic Report", ln=True, align='C')

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"Email: {email}", ln=True)
    pdf.cell(0, 10, f"Phone: {phone}", ln=True)
    pdf.cell(0, 10, f"OBD-II Code: {code}", ln=True)
    pdf.cell(0, 10, f"Urgency Level: {urgency} MPH", ln=True)
    pdf.multi_cell(0, 10, f"Advice: {advice}")

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Recommended Mechanics in Windsor:", ln=True)

    for mech in MECHANICS:
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 10, f"{mech['name']} - {mech['address']}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Visit www.read.codes for more info", ln=True)

    os.makedirs('reports', exist_ok=True)
    filename = f"CodeREAD_Report_{name.replace(' ', '_')}.pdf"
    path = os.path.join('reports', filename)
    pdf.output(path)
    return path

def send_email(recipient, attachment_path):
    msg = EmailMessage()
    msg['Subject'] = "Your CodeREAD Diagnostic Report"
    msg['From'] = "noreply@read.codes"
    msg['To'] = recipient
    msg.set_content("Attached is your CodeREAD report. Drive safe!")

    with open(attachment_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=os.path.basename(attachment_path))

    try:
        with smtplib.SMTP('localhost') as smtp:
            smtp.send_message(msg)
    except Exception as e:
        print(f"Email sending failed: {e}")

@app.route('/download/<path:filename>')
def download(filename):
    return send_file(os.path.join('reports', filename), as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
