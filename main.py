from flask import Flask, render_template, request
import openai
import os
import re

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def form():
    return render_template("form.html")

@app.route("/report", methods=["POST"])
def report():
    # Form fields
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    address = request.form.get("address", "")  # Optional
    vehicle_make = request.form["make"]
    vehicle_model = request.form["model"]
    vehicle_year = request.form["year"]
    code = request.form["codes"]

    # Build the prompt for AI
    prompt = f"""
    Generate a diagnostic report for OBD2 code {code}.
    Return clear, plain English answers for each section:
    1. Brief explanation of the code (technical + layman)
    2. Urgency level from 1–100
    3. Estimated repair cost in CAD
    4. Consequences of ignoring the issue
    5. Preventative care tips
    6. DIY repair potential
    7. Environmental impact
    8. Provide 3 relevant YouTube links:
       - code explanation
       - DIY fix
       - danger of ignoring it
    Make it readable and avoid repeating the code label itself constantly.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        output = response.choices[0].message["content"]

        def extract(label):
            match = re.search(rf"{label}[\.\):\-]*\s*(.*?)(?=\n\d+\.|\n$)", output, re.DOTALL)
            return match.group(1).strip() if match else "N/A"

        # Extract report fields
        explanation = extract("1")
        urgency = extract("2")
        cost = extract("3")
        consequences = extract("4")
        preventative = extract("5")
        diy = extract("6")
        environment = extract("7")

        # Get YouTube links
        video_links = re.findall(r'(https?://[^\s]+)', output)
        video_explanation = video_links[0] if len(video_links) > 0 else "#"
        video_diy = video_links[1] if len(video_links) > 1 else "#"
        video_consequences = video_links[2] if len(video_links) > 2 else "#"

        # Static mechanic list (for Windsor, for now)
        mechanic_1 = "Clover Auto – 4.7 stars – 519-555-1234"
        mechanic_2 = "Tecumseh Auto Repair – 4.6 stars – 519-555-5678"
        mechanic_3 = "Windsor Auto Pro – 4.8 stars – 519-555-9999"

        return render_template("report.html",
                               name=name,
                               email=email,
                               phone=phone,
                               address=address,
                               vehicle_make=vehicle_make,
                               vehicle_model=vehicle_model,
                               vehicle_year=vehicle_year,
                               code=code,
                               explanation=explanation,
                               urgency=urgency,
                               cost=cost,
                               consequences=consequences,
                               preventative=preventative,
                               diy=diy,
                               environment=environment,
                               video_explanation=video_explanation,
                               video_diy=video_diy,
                               video_consequences=video_consequences,
                               mechanic_1=mechanic_1,
                               mechanic_2=mechanic_2,
                               mechanic_3=mechanic_3)

    except Exception as e:
        return f"Error generating report: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
