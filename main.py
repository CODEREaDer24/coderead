from flask import Flask, request, render_template
import openai

app = Flask(__name__)

# One-time hardcoded OpenAI key for setup
openai.api_key = "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"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate-report", methods=["POST"])
def generate_report():
    name = request.form["name"]
    vehicle = request.form["vehicle"]
    code = request.form["code"]
    email = request.form["email"]

    try:
        # GPT-4 powered report
        prompt = f"""
You are a certified automotive technician. A customer has a vehicle showing OBD2 code {code}.
Generate a detailed diagnostic report that includes:
- Technical and plain-English explanation of the code
- Estimated repair costs in CAD
- Environmental impact
- Potential consequences of ignoring it
- Preventative tips
- DIY potential
- Urgency scale from 1–10

Vehicle: {vehicle}
Customer: {name}
"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        full_report = response.choices[0].message.content.strip()

    except Exception as e:
        full_report = f"Error generating report:\n\n{str(e)}"

    return render_template(
        "report.html",
        name=name,
        vehicle=vehicle,
        code=code,
        email=email,
        full_report=full_report
    )

if __name__ == "__main__":
    app.run(debug=True)
