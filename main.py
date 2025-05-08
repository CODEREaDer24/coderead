from flask import Flask, render_template, request
import openai
import os

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/report", methods=["POST"])
def report():
    name = request.form["name"]
    vehicle = request.form["vehicle"]
    code = request.form["code"]
    email = request.form["email"]

    prompt = f"Generate a diagnostic explanation for OBD2 code {code} on a {vehicle}."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    analysis = response["choices"][0]["message"]["content"]

    return render_template("index.html", name=name, vehicle=vehicle, code=code, email=email, analysis=analysis)

if __name__ == "__main__":
    app.run(debug=True)
