import os
from flask import Flask, request, render_template, send_file
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate-report", methods=["POST"])
def generate_report():
    name = request.form.get("name")
    vehicle = request.form.get("vehicle")
    code = request.form.get("code")
    email = request.form.get("email")

    # Create PDF in memory
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, f"Report for {name}")
    p.drawString(100, 730, f"Vehicle: {vehicle}")
    p.drawString(100, 710, f"Diagnostic Code: {code}")
    p.drawString(100, 690, f"Email: {email}")
    p.showPage()
    p.save()

    buffer.seek(0)

    # Return PDF as response
    return send_file(buffer, as_attachment=True, download_name="report.pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
