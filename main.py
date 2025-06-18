from flask import Flask, render_template, request

app = Flask(__name__)

MECHANICS = [
    {
        "name": "DLH Auto Service",
        "address": "2378 Central Ave, Windsor, ON N8W 4J2",
        "maps": "https://goo.gl/maps/xyz1"
    },
    {
        "name": "Demario’s Auto Clinic",
        "address": "2366 Dougall Ave, Windsor, ON N8X 1T1",
        "maps": "https://goo.gl/maps/xyz2"
    },
    {
        "name": "Kipping Tire & Automotive",
        "address": "1197 Ouellette Ave, Windsor, ON N9A 4K1",
        "maps": "https://goo.gl/maps/xyz3"
    }
]

@app.route("/", methods=["GET"])
def index():
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "Customer")
    email = request.form.get("email", "noemail@example.com")
    phone = request.form.get("phone", "")
    code = request.form.get("code", "P0420")

    urgency = 82
    layman = (
        "Your vehicle’s catalytic converter is not working properly. "
        "This means more pollution and lower engine efficiency."
    )
    technical = (
        "The oxygen sensor indicates the catalytic converter’s "
        "efficiency is below threshold, causing higher emissions."
    )
    consequences = (
        "Ignoring this can lead to failed emissions tests, increased "
        "fuel consumption, and potential engine damage."
    )
    cost_range = "$300 to $1200 depending on parts and labor."
    diy_possible = (
        "Replacing a catalytic converter is complex; better left to pros."
    )
    part_links = [
        {"label": "Catalytic Converter on Amazon", "url": "https://www.amazon.com/s?k=catalytic+converter"},
        {"label": "OBD-II Scanner on Amazon", "url": "https://www.amazon.com/s?k=obd+scanner"},
    ]
    youtube_link = "https://www.youtube.com/results?search_query=catalytic+converter+replacement"
    preventative = (
        "Regular engine tune-ups and fixing exhaust leaks help extend converter life."
    )

    return render_template(
        "report.html",
        name=name,
        email=email,
        phone=phone,
        code=code,
        urgency=urgency,
        layman=layman,
        technical=technical,
        consequences=consequences,
        cost_range=cost_range,
        diy_possible=diy_possible,
        part_links=part_links,
        youtube_link=youtube_link,
        mechanics=MECHANICS,
        preventative=preventative,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
