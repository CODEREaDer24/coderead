from flask import Flask, render_template, request, send_file
import io
import pdfkit

app = Flask(__name__)

# Hardcoded mechanic data
mechanics = [
    {"name": "Clover Auto Service", "address": "1130 Clover Ave", "phone": "(519) 979-1834"},
    {"name": "Tecumseh Auto Repair", "address": "11931 Tecumseh Rd E", "phone": "(519) 956-9190"},
    {"name": "Demario’s Auto Clinic", "address": "2366 Dougall Ave", "phone": "(519) 972-8383"},
]

# Sample diagnostic data for demo; in real use, this would come from DB or AI processing
sample_report = {
    "code": "P0171",
    "vehicle": "2015 Ford F-150",
    "layman": "Your engine is running with too much air and not enough fuel. It’s 'running lean', which can cause poor performance and long-term damage.",
    "youtube": "https://www.youtube.com/watch?v=MX3A1f-M_7I",
    "technical": "The PCM detected that the air-fuel mixture is too lean in Bank 1, often caused by vacuum leaks, faulty MAF sensor, or weak fuel delivery.",
    "consequences": [
        "Loss of power and acceleration",
        "Misfires and rough idle",
        "Damage to catalytic converter (expensive)",
        "Decreased fuel economy",
    ],
    "repair_cost": [
        "MAF sensor replacement: $120–$300",
        "Fuel injector cleaning/replacement: $90–$450",
        "Vacuum leak repair: $150–$350",
    ],
    "environmental_impact": "A lean-running engine burns fuel inefficiently, increasing emissions and possibly damaging pollution control systems.",
    "preventative": [
        "Replace air filter regularly",
        "Use quality fuel and fuel system cleaners",
        "Inspect vacuum lines annually for wear or cracks",
    ],
    "diy_level": "Moderate",
    "diy_link": "https://www.youtube.com/watch?v=WFxULjbnxig",
    "parts": [
        "Mass Air Flow (MAF) Sensor – $80–$150",
        "Fuel Injector Cleaner – $10–$20",
        "Vacuum Hose Kit – $25–$50",
    ],
}

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        code = request.form.get("engine_code", "").upper()
        city = request.form.get("city", "")
        vehicle_year = request.form.get("year", "")
        vehicle_make = request.form.get("make", "")
        vehicle_model = request.form.get("model", "")

        # Here you would replace this logic with your actual code lookup and processing
        # For now, return the sample report with replaced code and vehicle info
        report = sample_report.copy()
        report["code"] = code or sample_report["code"]
        report["vehicle"] = f"{vehicle_year} {vehicle_make} {vehicle_model}".strip() or sample_report["vehicle"]

        return render_template(
            "report.html",
            report=report,
            mechanics=mechanics,
        )
    return render_template("form.html")

@app.route("/download-pdf", methods=["POST"])
def download_pdf():
    html = request.form.get("html")
    if not html:
        return "No report content to generate PDF.", 400
    pdf = pdfkit.from_string(html, False)
    return send_file(
        io.BytesIO(pdf),
        download_name="CodeREAD_Report.pdf",
        mimetype="application/pdf",
        as_attachment=True,
    )

if __name__ == "__main__":
    app.run(debug=True)
