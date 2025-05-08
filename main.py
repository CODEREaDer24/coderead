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
    name = request.form["name"]
    vehicle = request.form["vehicle"]
    code = request.form["code"]
    email = request.form["email"]

    prompt = f"""
    You are CodeREAD's automotive AI. Generate a full diagnostic report for OBD2 code {code} on a {vehicle}.
    Include all sections clearly:
    1. Technical and layman's explanation
    2. Urgency level 1–10 + a brief urgency label
    3. Estimated repair cost in CAD
    4. Consequences of ignoring it
    5. Preventative maintenance tips
    6. DIY potential (and any cautions)
    7. Environmental impact
    8. Suggest 2 helpful YouTube video links with titles
    9. Recommend 3 mechanics in Windsor, Ontario with ratings
    Format each section clearly.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response["choices"][0]["message"]["content"]

    # --- Simple parsing (replace with better parsing later) ---
    def extract(section):
        if section in content:
            start = content.find(section) + len(section)
            end = content.find("\n", start)
            return content[start:end].strip()
        return "Data unavailable"

    explanation = content.split("1.")[1].split("2.")[0].strip()
    urgency_raw = content.split("2.")[1].split("3.")[0].strip()
    urgency_level = ''.join([c for c in urgency_raw if c.isdigit()]) or "N/A"
    urgency_label = urgency_raw.replace(urgency_level, '').strip(" -–")
    costs = content.split("3.")[1].split("4.")[0].strip()
    consequences = content.split("4.")[1].split("5.")[0].strip()
    tips = content.split("5.")[1].split("6.")[0].strip()
    diy = content.split("6.")[1].split("7.")[0].strip()
    impact = content.split("7.")[1].split("8.")[0].strip()

    # Videos
    video_block = content.split("8.")[1].split("9.")[0].strip().split("\n")
    videos = []
    for line in video_block:
        if "http" in line:
            parts = line.split("http")
            title = parts[0].strip(" -•")
            link = "http" + parts[1].strip()
            videos.append({"title": title, "link": link})

    # Mechanics
    mech_block = content.split("9.")[1].strip().split("\n")
    mechanics = []
    for line in mech_block:
        if "–" in line or "-" in line:
            sep = "–" if "–" in line else "-"
            name, rating = line.split(sep, 1)
            mechanics.append({"name": name.strip(), "rating": rating.strip()})

    return render_template("report.html",
                           name=name,
                           vehicle=vehicle,
                           code=code,
                           email=email,
                           urgency_level=urgency_level,
                           urgency_label=urgency_label,
                           explanation=explanation,
                           costs=costs,
                           consequences=consequences,
                           tips=tips,
                           diy=diy,
                           impact=impact,
                           videos=videos,
                           mechanics=mechanics)

if __name__ == "__main__":
    app.run(debug=True)
