from flask import Flask, request, render_template
import json
import os

app = Flask(__name__)

# Load enhanced diagnostic data
with open("parts_links.json") as f:
    parts_data = json.load(f)

@app.route("/", methods=["GET"])
def form():
    return render_template("form.html")

@app.route("/report", methods=["POST"])
def report():
    input_codes = request.form.get("codes", "").upper().replace(" ", "").split(",")
    matched = [item for code in input_codes for item in parts_data if item["code"] == code]

    if not matched:
        return "<h1>No matching codes found.</h1>"

    # Load report template manually since it's string-formatted
    report_template_path = os.path.join("templates", "report.html")
    with open(report_template_path) as f:
        report_template = f.read()

    report_sections = ""

    for item in matched:
        mechanics_html = "".join([
            f"<li><strong>{m['name']}</strong> – {m['rating']} stars – {m['contact']}</li>"
            for m in item["mechanics"]
        ])

        section = report_template.format(
            code=item["code"],
            issue_tech=item["issue_tech"],
            issue_plain=item["issue_plain"],
            urgency=item["urgency"],
            cost=item["cost"],
            consequences=item["consequences"],
            diy=item["diy"],
            impact=item["impact"],
            prevention=item["prevention"],
            part=item["part"],
            part_link=item["part_link"],
            video_link=item["video_link"],
            mechanics=mechanics_html
        )

        report_sections += f"<div class='code-section'>{section}</div><hr>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CodeREAD Full Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #fefefe; }}
            h1 {{ color: #C0392B; }}
            .code-section {{ margin-bottom: 40px; }}
            .urgency-meter {{
                width: 100%; background: #eee; border-radius: 10px; overflow: hidden;
                margin: 10px 0;
            }}
            .urgency-bar {{
                height: 20px; background: linear-gradient(to right, green, orange, red);
                width: 80%;
            }}
        </style>
    </head>
    <body>
        <h1>CodeREAD Diagnostic Report</h1>
        {report_sections}
    </body>
    </html>
    """
