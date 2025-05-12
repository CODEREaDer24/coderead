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
        Use the following exact structure with labels:
        1. Urgency Level: [1–100] – [Immediate, Fine for Now, Can Wait]
        2. Technical Explanation: [Text]
        3. Layman's Explanation: [Text]
        4. Estimated Repair Cost in CAD: [Text]
        5. Consequences of Not Fixing: [Text]
        6. Preventative Maintenance Tips: [Text]
        7. DIY Potential (and any cautions): [Text]
        8. Environmental Impact: [Text]
        9. Helpful Videos: [2 real YouTube links with titles]
        10. Mechanics: Only include:
            - Clover Auto – 4.8 Stars
            - Tecumseh Auto Repair – 4.6 Stars
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        content = response["choices"][0]["message"]["content"]
        logging.debug("GPT OUTPUT:\n" + content)

        def extract_between(text, start, end):
            try:
                return text.split(start)[1].split(end)[0].strip()
            except Exception:
                return "Data unavailable"

        urgency_block = extract_between(content, "1. Urgency Level:", "2. Technical Explanation:")
        urgency_match = re.search(r"(\d{1,3})\s*[-–]\s*(.*)", urgency_block)
        urgency_level = urgency_match.group(1) if urgency_match else "N/A"
        urgency_label = urgency_match.group(2).strip() if urgency_match else urgency_block

        technical = extract_between(content, "2. Technical Explanation:", "3. Layman's Explanation:")
        layman = extract_between(content, "3. Layman's Explanation:", "4. Estimated Repair Cost in CAD:")
        costs = extract_between(content, "4. Estimated Repair Cost in CAD:", "5. Consequences of Not Fixing:")
        consequences = extract_between(content, "5. Consequences of Not Fixing:", "6. Preventative Maintenance Tips:")
        tips = extract_between(content, "6. Preventative Maintenance Tips:", "7. DIY Potential (and any cautions):")
        diy = extract_between(content, "7. DIY Potential (and any cautions):", "8. Environmental Impact:")
        impact = extract_between(content, "8. Environmental Impact:", "9. Helpful Videos:")
        video_block = extract_between(content, "9. Helpful Videos:", "10. Mechanics:")

        videos = []
        for line in video_block.splitlines():
            if "http" in line:
                title, link = line.split("http", 1)
                videos.append({"title": title.strip(" -•"), "link": "http" + link.strip()})
            elif line.strip():
                videos.append({"title": line.strip(), "link": "#"})

        if not videos:
            videos.append({"title": "No videos found", "link": "#"})

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
