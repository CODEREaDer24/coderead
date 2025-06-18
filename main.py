from flask import Flask, render_template, request
app = Flask(__name__)

# Windsor mechanics hardcoded with map links
MECHANICS = [
    {
        "name": "DLH Auto Service",
        "address": "2378 Central Ave, Windsor, ON N8W 4J2",
        "maps": "https://goo.gl/maps/D6u6ftmGj76qTWEN8"
    },
    {
        "name": "Demario’s Auto Clinic",
        "address": "2366 Dougall Ave, Windsor, ON N8X 1T1",
        "maps": "https://goo.gl/maps/EvWvYqRH1zz4FpMu7"
    },
    {
        "name": "Kipping Tire & Automotive",
        "address": "1197 Ouellette Ave, Windsor, ON N9A 4K1",
        "maps": "https://goo.gl/maps/5WwrfHdhfFaUxyYq8"
    }
]

# Dummy data for demonstration - replace with real AI or lookup logic
def generate_report_data(code):
    # For example purposes only
    urgency_map = {
        "P0420": 75,
        "P0300": 90,
        "P0171": 50,
    }
    urgency = urgency_map.get(code.upper(), 40)
    return {
        "urgency": urgency,
        "layman": "This code means your vehicle's system is detecting a problem with emissions. It's not urgent but shouldn't be ignored.",
        "technical": "The catalytic converter efficiency is below threshold, likely due to a faulty oxygen sensor or converter degradation.",
        "consequences": "Ignoring this can cause increased emissions, potential failed inspections, and reduced fuel efficiency.",
        "cost_range": "$200 - $1500 depending on parts and labor.",
        "diy_possible": "Possible if you have moderate mechanical skills and tools. Oxygen sensor replacement is the common fix.",
        "part_links": [
            {"label": "Oxygen Sensor on Amazon", "url": "https://www.amazon.com/s?k=oxygen+sensor"},
            {"label": "Catalytic Converter on Amazon", "url": "https://www.amazon.com/s?k=catalytic+converter"},
        ],
        "youtube_link": "https://www.youtube.com/results?search_query=P0420+diagnostic+and+repair",
        "preventative": "Regular maintenance and using quality fuel can help prevent this issue.",
    }

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    year = request.form.get('year', '').strip()
    make = request.form.get('make', '').strip()
    model = request.form.get('model', '').strip()
    code = request.form.get('code', '').strip().upper()

    if not name or not email or not code or not year or not make or not model:
        error_msg = "All fields except phone are required. Please fill them in."
        return render_template('form.html', error=error_msg,
                               autofill={"name": name, "email": email, "phone": phone, "year": year, "make": make, "model": model, "code": code})

    report_data = generate_report_data(code)
    return render_template('report.html',
                           name=name,
                           email=email,
                           phone=phone,
                           year=year,
                           make=make,
                           model=model,
                           code=code,
                           urgency=report_data["urgency"],
                           layman=report_data["layman"],
                           technical=report_data["technical"],
                           consequences=report_data["consequences"],
                           cost_range=report_data["cost_range"],
                           diy_possible=report_data["diy_possible"],
                           part_links=report_data["part_links"],
                           youtube_link=report_data["youtube_link"],
                           mechanics=MECHANICS,
                           preventative=report_data["preventative"])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
