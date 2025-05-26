import os
import openai
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/report", methods=["POST"])
def report():
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    address = request.form.get("address", "")
    vehicle = request.form["vehicle"]
    code = request.form["code"]

    prompt = f"""You are CodeREAD, an expert auto technician. Create a diagnostic breakdown for OBD-II trouble code {code} using the format below:

1. Layman’s Explanation:
2. Urgency Scale (1–10):
3. Estimated Repair Cost (CAD):
4. Consequences of Ignoring:
5. Environmental Impact:
6. Preventative Care Tips:
7. DIY Potential:
8. YouTube Video (link):
9. Parts Link (Amazon or equivalent):
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        output = response["choices"][0]["message"]["content"]

        # Parse the response
        def extract(field, content):
            for line in content.split("\n"):
                if line.strip().lower().startswith(field.lower()):
                    return line.split(":", 1)[-1].strip()
            return "N/A"

        explanation = extract("Layman", output)
        urgency = extract("Urgency", output)
        repair_cost = extract("Repair", output)
        consequences = extract("Consequences", output)
        environment = extract("Environmental", output)
        prevention = extract("Preventative", output)
        diy = extract("DIY", output)
        diy_video_url = extract("YouTube", output)
        parts_link = extract("Parts", output)

        urgency_numeric = int(''.join(filter(str.isdigit, urgency)) or "5")
        urgency_gauge_url = f"/static/gauge_{urgency_numeric}.png"

    except Exception as e:
        explanation = "Report unavailable."
        urgency = "5"
        repair_cost = "N/A"
        consequences = "N/A"
        environment = "N/A"
        prevention = "N/A"
        diy = "N/A"
        diy_video_url = ""
        parts_link = ""
        urgency_gauge_url = "/static/gauge_5.png"

    mechanics = [
        {"name": "Clover Auto", "address": "1190 County Rd 42, Windsor, ON", "phone": "519-979-1834"},
        {"name": "Tecumseh Auto", "address": "5285 Tecumseh Rd E, Windsor, ON", "phone": "519-956-9190"},
        {"name": "DLH Auto Service", "address": "2378 Central Ave, Windsor, ON", "phone": "519-944-6516"},
        {"name": "Demario’s Auto Clinic", "address": "2366 Dougall Ave, Windsor, ON", "phone": "519-969-7922"},
        {"name": "Kipping Tire & Automotive", "address": "1197 Ouellette Ave, Windsor, ON", "phone": "519-254-9511"},
    ]

    return render_template("report.html",
                           name=name,
                           email=email,
                           phone=phone,
                           address=address,
                           vehicle=vehicle,
                           code=code,
                           urgency=urgency_numeric,
                           explanation=explanation,
                           repair_cost=repair_cost,
                           consequences=consequences,
                           environment=environment,
                           prevention=prevention,
                           diy=diy,
                           diy_video_url=diy_video_url,
                           parts_link=parts_link,
                           urgency_gauge_url=urgency_gauge_url,
                           mechanics=mechanics)

if __name__ == "__main__":
    app.run(debug=True)
