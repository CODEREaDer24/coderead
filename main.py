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

        prompt = f"Generate a detailed diagnostic report for OBD2 code {code} on a {vehicle}. Include: urgency (1-10), summary (tech + layman), cost (CAD), consequences, preventative care tips, DIY potential, environmental impact, and recommend a mechanic in Windsor. Format in HTML for a customer report. Use this customer info: Name: {name}, Email: {email}."

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        report = response.choices[0].message.content
        return report

    return render_template("form.html")
