from flask import Flask, render_template, request
import openai
import os
import re
import logging

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")
logging.basicConfig(level=logging.DEBUG)

@app.route("/", methods=["GET"])
def form():
    return render_template("form.html")

@app.route("/report", methods=["POST"])
def report():
    try:
        name = request.form["name"]
        vehicle = request.form["vehicle"]
        code = request.form["code"]
        email = request.form["email"]

        logging.debug(f"Received: name={name}, vehicle={vehicle}, code={code}, email={email}")

        prompt = f"""
        You are CodeREAD's automotive AI. Generate a full diagnostic report for OBD2 code {code} on a {vehicle}.
        Use the following section headers:
        1. Technical Explanation
        2. Layman's Explanation
        3. Urgency Level (1–100) with label (Immediate, Fine for Now, Can Wait)
        4. Estimated Repair Cost in CAD
        5. Consequences of Not Fixing
        6. Preventative Maintenance Tips
        7. DIY Potential (and any cautions)
        8. Environmental Impact
        9. YouTube Video Links with titles (2 real links if possible)
        10. Mechanics (only list these 2 in Windsor, Ontario):
            - Clover Auto – 4.8 Stars
            - Tecumseh Auto Repair – 4.6 Stars
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        content = response["choices"][0]["message"]["content"]
        logging.debug("GPT response received")

        def extract_between(text, start, end):
            try:
                return text.split(start)[1].split(end)[0].strip()
            except IndexError:
                return "Data unavailable"

        technical = extract_between(content, "1. Technical Explanation", "2. Layman's Explanation")
        layman = extract_between(content, "2. Layman's Explanation", "3. Urgency Level")
        urgency_block = extract_between(content, "3. Urgency Level", "4. Estimated Repair Cost")

        urgency_match = re.search(r"(\d{1,3})\s*[-–]\s*(.*)", urgency_block)
        if urgency_match:
            urgency_level = urgency_match.group(1)
            urgency_label = urgency_match.group(2).strip()
        else:
            urgency_level = "N/A"
            urgency_label = urgency_block.strip()

        costs = extract_between(content, "4. Estimated Repair Cost", "5. Consequences of Not Fixing")
        consequences = extract_between(content, "5. Consequences of Not Fixing", "6. Preventative Maintenance Tips")
        tips = extract_between(content, "6. Preventative Maintenance Tips", "7. DIY Potential")
        diy = extract_between(content, "7. DIY Potential", "8. Environmental Impact")
        impact = extract_between(content, "8. Environmental Impact", "9. YouTube Video Links")

        video_block = extract_between(content, "9. YouTube Video Links", "10. Mechanics")
        videos = []
        for line in video_block.splitlines():
            match = re.search(r"(.*)https?://(\S+)", line)
            if match:
                title = match.group(1).strip(" -•")
                link = "https://" + match.group(2).strip()
                videos.append({"title": title, "link": link})
            elif line.strip():  # no URL found
                videos.append({"title": line.strip(), "link": "#"})

        mechanics = [
            {"name": "Clover Auto", "rating": "4.8 Stars"},
            {"name": "Tecumseh Auto Repair", "rating": "4.6 Stars"}
        ]

        return render_template("report.html",
                               name=name,
                               vehicle=vehicle,
                               code=code,
                               email=email,
                               urgency_level=urgency_level,
                               urgency_label=urgency_label,
                               technical=technical,
                               layman=layman,
                               costs=costs,
                               consequences=consequences,
                               tips=tips,
                               diy=diy,
                               impact=impact,
                               videos=videos,
                               mechanics=mechanics)

    except Exception as e:
        logging.exception("Error generating report")
        return f"<h1>Internal Server Error</h1><p>{str(e)}</p>", 500

if __name__ == "__main__":
    app.run(debug=True)
