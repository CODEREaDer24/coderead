from flask import Flask, request, render_template
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        vehicle = request.form["vehicle"]
        code = request.form["code"]
        email = request.form["email"]

        # Send prompt to OpenAI for expanded parameters
        prompt = f"""
        For a {vehicle}, generate the following based on diagnostic code {code}:
        1. A technical explanation.
        2. A layman's explanation.
        3. An urgency rating from 1–10.
        4. Estimated cost range to repair in CAD.
        5. Consequences of not fixing the issue.
        6. Preventative maintenance tips.
        7. DIY potential (yes/no and why).
        8. Environmental impact (if any).
        9. A good video link that explains this code.
        10. A highly-rated mechanic in Windsor, Ontario (Clover Auto or Tecumseh Auto preferred).
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert vehicle diagnostics assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            reply = response.choices[0].message.content

            # Extract values manually from the response (rough parse)
            lines = reply.split('\n')
            data = {
                "name": name,
                "vehicle": vehicle,
                "code": code,
                "email": email,
                "tech_issue": lines[0].split(": ", 1)[-1],
                "plain_issue": lines[1].split(": ", 1)[-1],
                "urgency": lines[2].split(": ", 1)[-1],
                "cost_estimate": lines[3].split(": ", 1)[-1],
                "consequences": lines[4].split(": ", 1)[-1],
                "tips": lines[5].split(": ", 1)[-1],
                "diy": lines[6].split(": ", 1)[-1],
                "environment": lines[7].split(": ", 1)[-1],
                "video_url": lines[8].split(": ", 1)[-1],
                "mechanic": lines[9].split(": ", 1)[-1],
            }

        except Exception as e:
            return f"<h1>Error generating report:</h1><p>{str(e)}</p>"

        return render_template("report.html", **data)

    return render_template("form.html")
