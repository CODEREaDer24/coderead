from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

DB = "coderead_submissions.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            vin TEXT,
            symptoms TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit()

@app.route("/")
def form():
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    email = request.form["email"]
    vin = request.form["vin"]
    symptoms = request.form["symptoms"]

    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO submissions (name, email, vin, symptoms) VALUES (?, ?, ?, ?)",
                  (name, email, vin, symptoms))
        conn.commit()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
