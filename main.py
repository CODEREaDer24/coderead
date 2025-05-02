from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate-report", methods=["POST"])
def generate_report():
    name = request.form.get("name")
    vehicle = request.form.get("vehicle")
    code = request.form.get("code")
    email = request.form.get("email")

    print("Data received:", name, vehicle, code, email)

    return f"Report generated for {name} ({vehicle}) with code {code}. Confirmation sent to {email}."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
