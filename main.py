from flask import Flask, render_template, request, send_file
import pdfkit
import json
import os

app = Flask(__name__)

with open('parts_links.json') as f:
    PARTS_DB = json.load(f)

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/report', methods=['POST'])
def report():
    code = request.form['code'].upper()
    year = request.form['year']
    make = request.form['make']
    model = request.form['model']
    city = request.form.get('city', 'Windsor')

    # Hardcoded example for P0171
    if code == 'P0171':
        data = {
            "laymans": "Your engine is running with too much air and not enough fuel — it's 'running lean.' Like trying to run a marathon breathing through a straw.",
            "video_url": "https://www.youtube.com/watch?v=MX3A1f-M_7I",
            "technical": "PCM has detected a lean condition in Bank 1. Common causes: vacuum leaks, dirty MAF sensor, weak fuel delivery.",
            "consequences": [
                "Loss of power and acceleration",
                "Misfires and rough idle",
                "Catalytic converter damage (expensive)",
                "Poor fuel economy"
            ],
            "repair_costs": [
                "MAF sensor: $120–$300",
                "Fuel injector service: $90–$450",
                "Vacuum leak repair: $150–$350"
            ],
            "environmental": "A lean engine burns fuel inefficiently, causing excess emissions and possibly damaging emission controls.",
            "prevention": [
                "Replace air filter regularly",
                "Use quality fuel and cleaners",
                "Inspect vacuum lines annually"
            ],
            "diy_level": "Moderate",
            "diy_video_url": "https://www.youtube.com/watch?v=WFxULjbnxig",
            "parts": [
                "Mass Air Flow (MAF) Sensor – $80–$150",
                "Fuel Injector Cleaner – $10–$20",
                "Vacuum Hose Kit – $25–$50"
            ],
            "mechanics": [
                {"name": "DLH Auto Service", "address": "2378 Central Ave", "phone": "519-944-4400"},
                {"name": "Demario’s Auto Clinic", "address": "2366 Dougall Ave", "phone": "519-972-8383"},
                {"name": "Kipping Tire & Automotive", "address": "1197 Ouellette Ave", "phone": "519-252-2382"}
            ]
        }
    else:
        return "Code not recognized yet."

    return render_template('report.html', code=code, year=year, make=make, model=model, city=city, **data)

@app.route('/download')
def download():
    code = request.args.get('code', 'P0000')
    year = request.args.get('year', '2020')
    make = request.args.get('make', 'Unknown')
    model = request.args.get('model', 'Vehicle')
    city = request.args.get('city', 'Windsor')
    
    html = render_template('report.html', code=code, year=year, make=make, model=model, city=city,
        laymans="Sample",
        video_url="#",
        technical="Sample",
        consequences=["Sample"],
        repair_costs=["Sample"],
        environmental="Sample",
        prevention=["Sample"],
        diy_level="Sample",
        diy_video_url="#",
        parts=["Sample"],
        mechanics=[]
    )
    pdfkit.from_string(html, 'reports/report.pdf')
    return send_file('reports/report.pdf', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
