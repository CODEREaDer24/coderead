import os
from flask import Flask, request, render_template, send_file
from flask_mail import Mail, Message
from dotenv import load_dotenv
import openai
from xhtml2pdf import pisa
from io import BytesIO

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Mail config
app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
mail = Mail(app)

@app.route('/')
def home():
    return "CodeREAD server is live."

@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']
        vehicle_make = request.form['vehicle_make']
        vehicle_model = request.form['vehicle_model']
        vehicle_year = request.form['vehicle_year']
        obd_code = request.form['obd_code']

        # Run GPT analysis
        prompt = f"""Explain OBD2 code {obd_code} using these sections:
1. Technical explanation
2. Layman's explanation
3. Urgency (1–10)
4. Estimated repair cost in CAD
5. What happens if you ignore it
6. Preventative maintenance tips
7. Environmental impact
8. DIY repair potential
Format as HTML with <h2> headers and <p> paragraphs."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            analysis = response['choices'][0]['message']['content']
        except Exception as e:
            analysis = f"<h2>Error</h2><p>{str(e)}</p>"

        # Generate PDF from HTML
        rendered_html = render_template('report_template.html',
            customer_name=customer_name,
            address=address,
            phone=phone,
            email=email,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            vehicle_year=vehicle_year,
            obd_code=obd_code,
            analysis=analysis
        )
        pdf = BytesIO()
        pisa_status = pisa.CreatePDF(rendered_html, dest=pdf)

        if pisa_status.err:
            return "PDF generation failed"

        # Email the PDF
        try:
            msg = Message(
                subject=f"Your CodeREAD Diagnostic Report for {obd_code}",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.body = "Attached is your diagnostic report. Thank you for using CodeREAD!"
            msg.attach(f"{obd_code}_report.pdf", "application/pdf", pdf.getvalue())
            mail.send(msg)
        except Exception as e:
            return f"Email failed: {str(e)}"

        return "Report emailed successfully."

    return render_template('form.html')

if __name__ == '__main__':
    app.run()
