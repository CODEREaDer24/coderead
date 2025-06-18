from flask import Flask, render_template, request, send_file, Markup
import pdfkit
import tempfile
import os

app = Flask(__name__)

# Static mechanic data
mechanics = [
    {"name": "Clover Auto", "address": "5195 Clover Ave, Windsor, ON", "phone": "519-979-1834"},
    {"name": "Tecumseh Auto", "address": "1295 Walker Rd, Windsor, ON", "phone": "519-956-9190"},
    {"name": "Demario’s Auto Clinic", "address": "2366 Dougall Ave, Windsor, ON", "phone": "519-972-8383"}
]

# Sample report structure
sample_report = {
    "code": "P0171",
    "vehicle": "2014 Chevrolet Malibu",
    "layman": "Your engine is running lean – too much air, not enough fuel.",
    "youtube": "https://www.youtube.com/watch?v=MX3A1f-M_7I",
    "technical": "PCM detects a lean air/fuel ratio in Bank 1 – often due to vacuum leak, dirty MAF sensor, or low fuel pressure.",
    "consequences": [
        "Rough idle and hesitation",
        "Reduced performance",
        "Catalytic converter damage"
    ],
    "costs": [
        "MAF sensor replacement: $120–$300",
        "Vacuum leak repair: $150–$350",
        "Fuel pump replacement: $400–$700"
    ],
    "environment": "Leaner mix increases NOx emissions and can ruin catalytic converter.",
    "preventative": [
        "Inspect vacuum hoses regularly",
        "Use quality fuel",
        "Replace air filter annually"
    ],
    "diy": {
        "level": "Moderate",
        "video": "https://www.youtube.com/watch?v=WFxULjbnxig"
    },
    "parts": [
        {"name": "MAF Sensor", "price": "$85–$140"},
        {"name": "Vacuum Hose Kit", "price": "$30–$50"},
        {"name": "Fuel System Cleaner", "price": "$10–$20"}
    ]
}

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        code = request.form.get("engine_code", "").upper()
        city = request.form.get("city", "")
        year = request.form.get("year", "")
        make = request.form.get("make", "")
        model = request.form.get("model", "")
        
        report = sample_report.copy()
        report["code"] = code or sample_report["code"]
        report["vehicle"] = f"{year} {make} {model}".strip() or sample_report["vehicle"]

        html_content = render_template("report_content.html", report=report, mechanics=mechanics)
        return render_template("report.html", report=report, report_html=Markup(html_content), mechanics=mechanics)

    return render_template("form.html")

@app.route("/download-pdf", methods=["POST"])
def download_pdf():
    html = request.form.get("html", "")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        pdfkit.from_string(html, f.name)
        return send_file(f.name, as_attachment=True, download_name="CodeREAD_Report.pdf")
