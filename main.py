import os
import openai
from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import tempfile
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

def safe_text(text):
    return text.encode("latin-1", "replace").decode("latin-1")

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(255, 204, 0)
        self.cell(0, 10, "CodeREAD Diagnostic Report", ln=True, align="C")

    def section(self, title, content, link=None):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(255, 204, 0)
        self.cell(0, 10, safe_text(title), ln=True)
        self.set_font("Helvetica", "", 12)
        self.set_text_color(255, 255, 255)
        if link:
            self.set_text_color(74, 168, 255)
            self.cell(0, 10, safe_text(content), ln=True, link=link)
        else:
            self.multi_cell(0, 10, safe_text(content))

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
        result = response.choices[0].message.content
    except Exception as e:
        result = f"Error: {str(e)}"

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_fill_color(26, 26, 26)
    pdf.section("Customer Info", f"{name} | {email} | {phone} | {address} | {vehicle}")
    pdf.section(f"Trouble Code: {code}", result)

    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf').name
    pdf.output(temp_path)
    return send_file(temp_path, as_attachment=True, download_name=f"{code}_CodeREAD_Report.pdf")

if __name__ == '__main__':
    app.run(debug=True)
