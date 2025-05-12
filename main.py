from flask import Flask, render_template, request
import openai
import os

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def form():
    return render_template("form.html")

@app.route("/report", methods=["POST"])
def report():
    # Gather form inputs
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    address = request.form["address"]
    vehicle_make = request.form["make"]
    vehicle_model = request.form["model"]
    vehicle_year = request.form["year"]
    code = request.form["codes"]

    # AI prompt to analyze the OBD2 code
    prompt = f"""
    Generate a diagnostic report for OBD2 code {code}.
    Include the following sections:
    1. Technical explanation (clear and layman-friendly)
    2. Urgency level from 1–100
    3. Estimated repair cost in CAD
    4. Consequences of ignoring
    5. Preventative care tips
    6. DIY repair potential
    7. Environmental impact
    8. 3 YouTube video links: 
       - explanation of the code, 
       - DIY repair, 
       - why it's dangerous to ignore
    Output all content in plain text, labeled clearly.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        output = response.choices[0].message["content"]

        # Basic parsing (assuming consistent format — can upgrade later)
        def extract(label):
            marker = f"{label}:"
            start = output.find(marker) + len(marker)
            end = output.find("\n", start)
            return output[start:end].strip()

        explanation = extract("1. Technical explanation")
        urgency = extract("2. Urgency level")
        cost = extract("3. Estimated repair cost")
        consequences = extract("4. Consequences of ignoring")
        preventative = extract("5. Preventative care tips")
        diy = extract("6. DIY repair potential")
        environment = extract("7. Environmental impact")
        
        # Grab 3 URLs
        video_links = [line.strip() for line in output.split("\n") if "http" in line]
        video_explanation = video_links[0] if len(video_links) > 0 else "#"
        video_diy = video_links[1] if len(video_links) > 1 else "#"
        video_consequences = video_links[2] if len(video_links) > 2 else "#"

        # Recommended mechanics (hardcoded for now — later AI/local DB)
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
        return f"Error generating report: {e}"

if __name__ == "__main__":
    app.run(debug=True)
