import os
import logging
from flask import Flask, render_template, request, send_file
import openai
from fpdf import FPDF
import tempfile
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Email credentials (Render environment vars or .env)
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

logging.basicConfig(level=logging.INFO)

# Globals for latest report
last_report_text = ""
last_diagnostic_code = ""
last_pdf_path = ""
last_email = ""

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/report', methods=['POST'])
def report():
    global last_report_text, last_diagnostic_code, last_pdf_path, last_email

    try:
        name = request.form.get('name', '')
        last_email = request.form.get('email', '')
        make = request.form.get('make', '')
        model = request.form.get('model', '')
        year = request.form.get('year', '')
        codes_raw = request.form.get('codes', '')
        codes = [c.strip().upper() for c in codes_raw.split(',') if c.strip()]
        last_diagnostic_code = codes[0] if codes else 'P0000'

        print("DEBUG -- Name:", name)
        print("DEBUG -- Email:", last_email)
        print("DEBUG -- Codes:", codes)

        if not codes:
            raise ValueError("No valid codes provided")

        # GPT Prompt
        prompt = f"""
You are CodeREAD, an expert AI diagnostic assistant. The customer provided:
Vehicle: {year} {make} {model}
Codes: {', '.join(codes)}
Name: {name}

For each code, provide:
- Technical explanation
- Layman explanation
- Urgency (1–10)
- Repair cost (CAD)
- Consequences of ignoring
- Preventative care tips
- DIY potential
- Environmental impact
- AI Recommendation

Then summarize how these codes might be related.
"""

        print("DEBUG -- Prompt sent to GPT:", prompt)

        # --- Uncomment for live GPT ---
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        gpt_output = response['choices'][0]['message']['content'].strip()

        # --- Uncomment for testing without GPT ---
        # gpt_output = f"""This is a TEST CodeREAD report for {year} {make} {model} with code(s) {', '.join(codes)}."""

        print("DEBUG -- GPT Output:", gpt_output)

        if not gpt_output:
            raise ValueError("GPT returned empty response")

        last_report_text = gpt_output

        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(253, 216, 53)
        pdf.cell(200, 10, "CodeREAD Diagnostic Report", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(30, 30, 30)

        lines = gpt_output.split('\n')
        for line in lines:
            if line.strip():
                pdf.multi_cell(0, 10, line)

        # Helpful Links
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(253, 216, 53)
        pdf.cell(0, 10, "Helpful Links", ln=True)

        code = last_diagnostic_code
        links = [
            ("Watch Repair on YouTube", f"https://www.youtube.com/results?search_query=how+to+fix+{code}"),
            ("Find Parts on Amazon", f"https://www.amazon.ca/s?k={code}+car+part"),
            ("Search Local Mechanics", "https://maps.google.com/?q=mechanic+near+me")
        ]

        pdf.set_font("Arial", '', 12)
        pdf.set_text_color(0, 0, 255)
        for label, url in links:
            pdf.cell(0, 10, label, ln=True, link=url)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp_file.name)
        last_pdf_path = temp_file.name

        if EMAIL_SENDER and EMAIL_PASSWORD:
            send_email_with_pdf(name, last_email, temp_file.name)

        return render_template('report.html', report=gpt_output, diagnostic_code=code, error=None)

    except Exception as e:
        error_msg = f"Error generating report: {str(e)}"
        logging.error(error_msg)
        return render_template('report.html', report=None, error=error_msg)

@app.route('/download-pdf')
def download_pdf():
    if not last_pdf_path or not os.path.exists(last_pdf_path):
        return "PDF not found", 404
    return send_file(last_pdf_path, as_attachment=True, download_name="CodeREAD_Report.pdf")

def send_email_with_pdf(name, to_email, pdf_path):
    try:
        msg = EmailMessage()
        msg['Subject'] = f"Your CodeREAD Diagnostic Report"
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        msg.set_content(f"Hi {name},\n\nYour CodeREAD diagnostic report is attached.\n\n- CodeREAD")

        with open(pdf_path, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename="CodeREAD_Report.pdf")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        logging.info(f"Report emailed to {to_email}")

    except Exception as e:
        logging.error(f"Email send failed: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
