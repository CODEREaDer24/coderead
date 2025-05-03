from flask import Flask, request, render_template
import os
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        vehicle = request.form.get("vehicle")
        code = request.form.get("code")
        email = request.form.get("email")

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional automotive diagnostics expert."},
                    {"role": "user", "content": f"Generate a diagnostic report for OBD2 code {code} on a {vehicle}."}
                ]
            )
            analysis = response.choices[0].message.content
        except Exception as e:
            analysis = f"Error generating analysis: {str(e)}"

        return render_template("report.html", name=name, vehicle=vehicle, code=code, email=email, analysis=analysis)

    return render_template("form.html")

if __name__ == "__main__":
    app.run(debug=True)
