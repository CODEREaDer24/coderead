from flask import Flask, request, render_template
from openai import OpenAI
import os
import json

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        vehicle = request.form["vehicle"]
        code = request.form["code"]
        email = request.form["email"]

        try:
            prompt = f"""
You are CodeREAD AI. Generate a structured JSON object based on the following OBD2 trouble code and vehicle:

Vehicle: {vehicle}
Code: {code}

Output ONLY JSON with the following keys:
- urgency (1–10)
- layman
- cost_estimate
- consequences
- preventative_tips
- diy_potential
- environmental_impact
- recommended_mechanic (Clover Auto or Tecumseh Auto, Windsor preferred)
- video_link

Example format:
{{
  "urgency": 6,
  "layman": "This means...",
  "cost_estimate": "$350–$600 CAD",
  "consequences": "Engine wear and emissions increase...",
  "preventative_tips": "Check and replace sensors regularly...",
  "diy_potential": "Low. Requires professional tools.",
  "environmental_impact": "Higher emissions, fuel waste",
  "recommended_mechanic": "Clover Auto, Windsor",
  "video_link": "https://youtube.com/example"
}}
"""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            content = response.choices[0].message.content.strip()
            data = json.loads(content)

        except Exception as e:
            return render_template("report.html", name=name, vehicle=vehicle, code=code, email=email,
                                   urgency="Error", layman=str(e), cost_estimate="",
                                   consequences="", preventative_tips="", diy_potential="",
                                   environmental_impact="", recommended_mechanic="", video_link="")

        return render_template("report.html", name=name, vehicle=vehicle, code=code, email=email,
                               urgency=data.get("urgency", "N/A"),
                               layman=data.get("layman", ""),
                               cost_estimate=data.get("cost_estimate", ""),
                               consequences=data.get("consequences", ""),
                               preventative_tips=data.get("preventative_tips", ""),
                               diy_potential=data.get("diy_potential", ""),
                               environmental_impact=data.get("environmental_impact", ""),
                               recommended_mechanic=data.get("recommended_mechanic", ""),
                               video_link=data.get("video_link", ""))

    return render_template("form.html")

if __name__ == "__main__":
    app.run(debug=True)
