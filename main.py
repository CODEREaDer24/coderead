from flask import Flask, render_template, request, send_file
import pdfkit
import io

app = Flask(__name__)

# Dummy local mechanics data keyed by city (expand as needed)
LOCAL_MECHANICS = {
    "windsor": [
        {"name": "DLH Auto Service", "address": "2378 Central Ave, Windsor, ON N8W 4J2", "phone": "519-979-1834"},
        {"name": "Demario’s Auto Clinic", "address": "2366 Dougall Ave, Windsor, ON N8X 1T1", "phone": "519-956-9190"},
        {"name": "Kipping Tire & Automotive", "address": "1197 Ouellette Ave, Windsor, ON N9A 4K1", "phone": "519-254-1151"},
    ]
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        city = request.form.get("city", "").strip().lower()

        # Fake data for demo purposes, replace with your real data source
        report_data = generate_report_for_code(code)

        # Get local mechanics or empty list
        mechanics = LOCAL_MECHANICS.get(city, [])

        return render_template("report.html", code=code, report=report_data, mechanics=mechanics)
    return render_template("form.html")

def generate_report_for_code(code):
    # This is a hardcoded example - replace with DB or API calls in prod
    if code == "P0101":
        return {
            "layman": {
                "text": "Your car's airflow sensor is misreading air intake, causing rough idling or poor performance.",
                "video": "https://www.youtube.com/watch?v=FAKE_VIDEO_P0101"
            },
            "technical": "P0101 means the Mass Air Flow (MAF) sensor output is out of expected range based on RPM and throttle input.",
            "consequences": (
                "Ignoring this can lead to reduced fuel efficiency, engine stalling, "
                "and damage to the catalytic converter."
            ),
            "cost": {
                "parts": "$60–$120",
                "labor": "$77–$132",
                "total_shop": "$137–$252",
                "total_diy": "$60–$120"
            },
            "environmental": "Increased emissions and failed smog checks are common.",
            "prevention": "Regular air filter changes and sensor cleaning can help prevent this.",
            "diy": {
                "level": "Moderate 🟡",
                "video": "https://www.youtube.com/watch?v=DIY_P0101_REPAIR"
            },
            "parts_needed": [
                {"name": "MAF Sensor", "price": "$60–$120"},
                {"name": "Intake Hose", "price": "$15–$40"},
                {"name": "Throttle Body Cleaner", "price": "$10–$15"},
            ]
        }
    # Default fallback
    return {
        "layman": {"text": "No info available for this code.", "video": ""},
        "technical": "",
        "consequences": "",
        "cost": {},
        "environmental": "",
        "prevention": "",
        "diy": {"level": "Unknown", "video": ""},
        "parts_needed": []
    }

if __name__ == "__main__":
    app.run(debug=True)
