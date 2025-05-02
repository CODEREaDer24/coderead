from flask import Flask, request, render_template
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate-report", methods=["POST"])
def generate_report():
    name = request.form.get("name")
    vehicle = request.form.get("vehicle")
    code = request.form.get("code")
    email = request.form.get("email")

    # Create smart GPT prompt
    prompt = f"""
    Generate a diagnostic report for the following vehicle and trouble code.

    Vehicle: {vehicle}
    Diagnostic Code: {code}

    Provide:
    - A plain-language explanation and technical explanation
    - CodeREAD urgency scale (1–10)
    - Estimated repair cost in CAD
    - Consequences of ignoring the issue
    - Preventative care tips
    - DIY potential
    - Environmental impact
    - YouTube video links (if available)
    - 2 recommended Windsor-area mechanics: Clover Auto and Tecumseh Auto
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        report = response["choices"][0]["message"]["content"]
    except Exception as e:
        report = f"Error generating report: {e}"

    return render_template("report.html", name=name, vehicle=vehicle, code=code, email=email, full_report=report)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
