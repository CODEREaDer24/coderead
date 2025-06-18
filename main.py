import os
from flask import Flask, render_template, request, abort, send_file
import pdfkit
import logging
from datetime import datetime

app = Flask(__name__)

# Setup logging - this will log to console and file 'app.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Basic input validation
def validate_input(form):
    required_fields = ['name', 'email', 'city', 'year', 'make', 'model', 'code']
    for field in required_fields:
        if not form.get(field):
            return f"Missing required field: {field}"
    # Add more validations here if needed (e.g., email format, code format)
    return None

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Validate inputs
    error = validate_input(request.form)
    if error:
        logging.warning(f"Validation error: {error}")
        return f"<h2>Error: {error}</h2><p><a href='/'>Go back</a></p>", 400

    data = {
        'name': request.form['name'].strip(),
        'email': request.form['email'].strip(),
        'phone': request.form.get('phone', '').strip(),
        'city': request.form['city'].strip(),
        'year': request.form['year'].strip(),
        'make': request.form['make'].strip(),
        'model': request.form['model'].strip(),
        'code': request.form['code'].strip().upper(),
        'video_link': f"https://www.youtube.com/results?search_query=OBD2+code+{request.form['code'].strip().upper()}"
    }

    # Render HTML report
    try:
        rendered_html = render_template('report.html', **data)
    except Exception as e:
        logging.error(f"Template rendering error: {e}")
        abort(500, description="Internal server error rendering report")

    # Save HTML report for record-keeping
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = 'reports'
    os.makedirs(report_dir, exist_ok=True)
    report_filename = f"{report_dir}/report_{timestamp}.html"
    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        logging.info(f"Saved HTML report: {report_filename}")
    except Exception as e:
        logging.error(f"Failed to save report HTML: {e}")

    # Generate PDF (optional)
    try:
        pdf_filename = f"{report_dir}/report_{timestamp}.pdf"
        pdfkit.from_string(rendered_html, pdf_filename)
        logging.info(f"Generated PDF report: {pdf_filename}")
    except Exception as e:
        logging.error(f"PDF generation failed: {e}")
        pdf_filename = None

    # Return HTML report with a link to download PDF if created
    pdf_link_html = ''
    if pdf_filename and os.path.exists(pdf_filename):
        pdf_link_html = f'<p><a href="/download/{os.path.basename(pdf_filename)}" target="_blank">Download PDF Report</a></p>'

    return rendered_html + pdf_link_html

@app.route('/download/<filename>')
def download_report(filename):
    path = os.path.join('reports', filename)
    if not os.path.exists(path):
        abort(404, description="Report not found")
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
