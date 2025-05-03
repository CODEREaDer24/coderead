from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return "<h2>Welcome to CodeREAD. To generate a sample report, go to <a href='/generate'>/generate</a></h2>"

@app.route('/generate')
def generate():
    return render_template("report.html",
        name="Ciaran Ganley",
        vehicle="Ford F-150",
        code="P0429",
        email="deependpools@ymail.com",
        urgency="6",
        urgency_explanation="Moderate concern – emissions system not warming up efficiently.",
        tech_summary="The P0429 code is triggered by poor performance in the catalytic converter heater circuit.",
        layman_summary="Your emissions system isn’t warming up fast enough, which can fail tests and harm the engine over time.",
        repair_cost="Estimate: $600–$2,000 CAD depending on parts and labour.",
        consequences="Vehicle may fail emissions testing. Long-term engine damage if ignored.",
        preventative_tips="Drive longer trips occasionally to help the system reach operating temp. Regular checkups help.",
        diy_potential="Low. Diagnosis and fix often require a mechanic with proper tools.",
        environmental_impact="Increased emissions and lower fuel efficiency.",
        recommended_mechanic="Clover Auto & Tecumseh Auto (Windsor).",
        video_link="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )

if __name__ == '__main__':
    app.run(debug=True)
