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

# Email credentials (use environment vars on Render)
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

logging.basicConfig(level=logging.INFO)

# Store last report for download
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

        if not codes:
            raise ValueError("No valid codes provided")

        # Prompt GPT
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

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        gpt_output = response['choices'][0]['message']['content'].strip()
        last_report_text = gpt_output

        # Build PDF with branding
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(253, 216, 53)
        pdf.cell(200, 10, "CodeREAD Diagnostic Report", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(30, 30, 30)
        pdf.set_draw_color(253, 216, 53)

        lines = gpt_output.split('\n')
        for line in lines:
            if line.strip():
                pdf.multi_cell(0, 10, line, border=0)

        # Helpful links section
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

        # Save PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp_file.name)
        last_pdf_path = temp_file.name

        # Email the report
        if EMAIL_SENDER and EMAIL_PASSWORD:
            send_email_with_pdf(name, last_email, temp_file.name)

        return render_template('report.html', report=gpt_output, diagnostic_code=code, error=None)

    except Exception as e:
        logging.error("Error in report generation: %s", str(e))
        return render_template('report.html', report=None, error="Something went wrong while generating the report.")

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
        msg.set_content(f"Hi {name},\n\nYour CodeREAD diagnostic report is attached as a PDF.\n\nThanks,\nThe CodeREAD Team")

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
