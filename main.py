import os
import tempfile
import openai
from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import unicodedata

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

last_pdf_path = ""
last_report_text = ""

def clean(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/report', methods=['POST'])
def report():
    global last_pdf_path, last_report_text

    name = clean(request.form['name'])
    email = clean(request.form['email'])
    phone = clean(request.form['phone'])
    address = clean(request.form.get('address', 'N/A'))
    vehicle_make = clean(request.form['vehicle_make'])
    vehicle_model = clean(request.form['vehicle_model'])
    vehicle_year = clean(request.form['vehicle_year'])
    diagnostic_codes = clean(request.form['diagnostic_codes'])

    prompt = f"""
You are CodeREAD AI. Create a formatted diagnostic report for:

Name: {name}
Email: {email}
Phone: {phone}
Address: {address}
Vehicle: {vehicle_year} {vehicle_make} {vehicle_model}
Codes: {diagnostic_codes}

For each code include:
- Urgency (1–10, show this first)
- Technical Explanation
- Layman's Explanation
- Estimated Repair Cost (CAD)
- Consequences of Not Fixing
- Preventative Tips
- DIY Potential
- Environmental Impact
- Video link
- CodeREAD AI Recommendation
- Then restate name, phone, and address under each code
- Recommend 3 Windsor mechanics with name + phone
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a car diagnostics expert writing CodeREAD reports in clear HTML."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        report_text = response['choices'][0]['message']['content']
        last_report_text = report_text

        # PDF logic
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=11)
        cleaned_text = clean(report_text)

        pdf.set_fill_color(0, 0, 0)
        pdf.set_text_color(255, 255, 0)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "CodeREAD Diagnostic Report", ln=True, align='C', fill=True)
        pdf.ln(5)

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 8, cleaned_text)

        _, path = tempfile.mkstemp(suffix=".pdf")
        pdf.output(path)
        last_pdf_path = path

        return render_template("report.html", report_text=report_text)

    except Exception as e:
        return f"Error: {e}"

@app.route('/download')
def download():
    if last_pdf_path and os.path.exists(last_pdf_path):
        return send_file(last_pdf_path, as_attachment=True, download_name="CodeREAD_Report.pdf")
    return "No PDF found."
