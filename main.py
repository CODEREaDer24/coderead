from flask import Flask, request, render_template
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form["name"]
        vehicle = request.form["vehicle"]
        code = request.form["code"]
        email = request.form["email"]

        try:
            chat_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a vehicle diagnostics expert."},
                    {"role": "user", "content": f"Generate a diagnostic report for code {code} on a {vehicle}."}
                ]
            )
            analysis = chat_response.choices[0].message.content
        except Exception as e:
            analysis = f"Error generating analysis: {str(e)}"

        return render_template("report.html", name=name, vehicle=vehicle, code=code, email=email, analysis=analysis)

    return render_template("form.html")

if __name__ == "__main__":
    app.run(debug=True)
