from flask import Flask, render_template, request, send_file, redirect, url_for, session
import os
import datetime
import pdfkit

app = Flask(__name__)
app.secret_key = "coderead_secret"
app.config['UPLOAD_FOLDER'] = 'reports'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        code = request.form.get("code")
        year = request.form.get("year")
        make = request.form.get("make")
        model = request.form.get("model")

        if not name or not email or not code:
            return "Missing required fields", 400

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_id = f"{name}_{timestamp}".replace(" ", "_").replace(":", "-")

        session['report_data'] = {
            "name": name,
            "email": email,
            "phone": phone,
            "code": code,
            "year": year,
            "make": make,
            "model": model,
            "timestamp": timestamp,
            "report_id": report_id
        }

        return redirect(url_for('loading'))

    return render_template("form.html")

@app.route("/loading")
def loading():
    return render_template("loading.html")

@app.route("/report")
def report():
    data = session.get('report_data')
    if not data:
        return redirect(url_for('index'))

    html = render_template("report.html", **data)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{data['report_id']}.pdf")
    pdfkit.from_string(html, pdf_path)

    return render_template("report.html", **data)

@app.route("/pdf/<report_id>")
def get_pdf(report_id):
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{report_id}.pdf")
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    return "PDF not found", 404

if __name__ == "__main__":
    app.run(debug=True)
