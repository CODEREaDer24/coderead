import os
import openai
from flask import Flask, render_template, request, send_file
from dotenv import load_dotenv
from fpdf import FPDF
import tempfile

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

def safe_text(text):
    return text.encode("latin-1", "replace").decode("latin-1")

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/report', methods=['POST'])
def report():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    vehicle = request.form['vehicle']
    code = request.form['code'].strip().upper()

    prompt = f"""You are CodeREAD AI. Break down OBD2 trouble code {code} for a {vehicle}.
Return full report with:
- Layman's Explanation
- Technical Explanation
- Urgency (1–10)
- Estimated CAD Repair Cost
- Consequences if Ignored
- Preventative Tips
- DIY Potential
- Environmental Impact
- Code Explanation YouTube Link
- DIY Repair YouTube Link
- Recommended Amazon Parts Link
- CodeREAD AI Final Recommendation"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            timeout=30
        )
        gpt_text = response.choices[0].message.content
    except Exception as e:
        gpt_text = f"Error: {str(e)}"

    # Create PDF copy
    class PDF(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 16)
            self.set_text_color(255, 204, 0)
            self.cell(0, 10, "CodeREAD Diagnostic Report", ln=True, align="C")

        def section(self, title, content):
            self.set_font("Helvetica", "B", 14)
            self.set_text_color(255, 204, 0)
            self.cell(0, 10, safe_text(title), ln=True)
            self.set_font("Helvetica", "", 12)
            self.set_text_color(255, 255, 255)
            self.multi_cell(0, 10, safe_text(content))

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_fill_color(26, 26, 26)
    pdf.section("Customer Info", f"{name} | {email} | {phone} | {address} | {vehicle}")
    pdf.section(f"Trouble Code: {code}", gpt_text)

    temp_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf').name
    pdf.output(temp_pdf_path)

    return render_template(
        'report.html',
        name=name,
        email=email,
        phone=phone,
        address=address,
        vehicle=vehicle,
        code=code,
        result=gpt_text,
        pdf_path=temp_pdf_path
    )

@app.route('/download')
def download():
    path = request.args.get('path')
    return send_file(path, as_attachment=True, download_name="CodeREAD_Report.pdf")

if __name__ == '__main__':
    app.run(debug=True)
