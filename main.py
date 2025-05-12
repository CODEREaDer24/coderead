from flask import Flask, request, render_template_string
import json

app = Flask(__name__)

with open("parts_links.json") as f:
    parts_data = json.load(f)

@app.route("/", methods=["GET"])
def form():
    return render_template_string(open("form.html").read())

@app.route("/report", methods=["POST"])
def report():
    code = request.form.get("code").strip().upper()
    match = next((item for item in parts_data if item["code"] == code), None)
    if not match:
        return f"<h1>Code {code} not found</h1>"
    return render_template_string(open("report.html").read(), **match)
