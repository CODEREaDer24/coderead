from flask import Flask, request, render_template
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        vehicle = request.form["vehicle"]
        code = request.form["code"]
        email = request.form["email"]

        prompt = f"Generate a detailed diagnostic report for OBD2 code {code} on a {vehicle}. Include: urgency (1–10), summary (tech + layman), estimated repair cost (CAD), consequences of not fixing it, preventative care tips, DIY potential, environmental impact, and recommend a mechanic in Windsor. Format in HTML as a clean customer-facing diagnostic report. Include: Name: {name}, Email: {email}."

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        report = response.choices[0].message['content']
        return report

    return render_template("form.html")
