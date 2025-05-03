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

        prompt = (
            f"You are CodeREAD AI. Create a full vehicle diagnostic report for OBD2 code {code} "
            f"on a {vehicle}. Include:\n"
            "- Urgency scale (1–10) with explanation and color scale\n"
            "- Technical and layman issue summaries\n"
            "- Estimated repair cost in CAD\n"
            "- Consequences of ignoring\n"
            "- Preventative tips\n"
            "- DIY potential\n"
            "- Environmental impact\n"
            "- Recommend a real Windsor mechanic (Tecumseh Auto or Clover Auto)\n"
            "- Link to a real YouTube video about this code on a Ford F150\n"
            "Output full structured HTML. Be detailed but professional."
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            analysis = response.choices[0].message.content
            return render_template("report.html", name=name, vehicle=vehicle, code=code, email=email, analysis=analysis)

        except Exception as e:
            return f"Error generating report: {str(e)}"

    return render_template("form.html")

if __name__ == "__main__":
    app.run(debug=True)
