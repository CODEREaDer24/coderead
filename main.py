import os
from flask import Flask, request, render_template

app = Flask(__name__)

# Home route – renders index.html
@app.route("/")
def home():
    return render_template("index.html")

# Route to handle form submissions
@app.route("/generate-report", methods=["POST"])
def generate_report():
    name = request.form.get("name")
    vehicle = request.form.get("vehicle")
    code = request.form.get("code")
    email = request.form.get("email")

    # Log incoming data (for debug purposes)
    print("Data received:", name, vehicle, code, email)

    # Placeholder response (replace with PDF generation or email logic)
    return f"""
    <h2>Report Generated</h2>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Vehicle:</strong> {vehicle}</p>
    <p><strong>Diagnostic Code:</strong> {code}</p>
    <p><strong>Email:</strong> {email}</p>
    <br>
    <a href="/">Back to Home</a>
    """

# Run locally (ignored by Render in production)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
