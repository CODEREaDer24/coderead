from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DB = "coderead_submissions.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                vin TEXT,
                symptoms TEXT,
                codes TEXT,
                urgency TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

@app.route("/")
def form():
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    email = request.form.get("email")
    vin = request.form.get("vin")
    symptoms = request.form.get("symptoms")
    codes = request.form.get("codes", "")
    urgency = request.form.get("urgency", "Unknown")

    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO submissions (name, email, vin, symptoms, codes, urgency)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, vin, symptoms, codes, urgency))
        conn.commit()

    return redirect(url_for("report", vin=vin))

@app.route("/report")
def report():
    vin = request.args.get("vin")
    if not vin:
        return "VIN not provided.", 400

    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM submissions WHERE vin = ? ORDER BY timestamp DESC LIMIT 1", (vin,))
        row = c.fetchone()

    if not row:
        return "Submission not found.", 404

    data = dict(row)
    data["codes"] = data.get("codes", "").split(",")
    return render_template("report.html", data=data)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
