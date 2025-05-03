from flask import Flask, render_template, request
import os
import openai
import re

app = Flask(__name__)

# Load OpenAI key from environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Homepage route – serves the diagnostic form
@app.route('/')
def index():
    return render_template('form.html')

# Helper: Extract each section using markdown-style labels
def extract_section(label, text):
    pattern = rf"\*\*{label}:\*\*\s*(.*?)(?=\n\*\*|\Z)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else "–"

# Generate report from form input
@app.route('/generate', methods=['POST'])
def generate():
    name = request.form.get('name', 'Unknown')
    email = request.form.get('email', 'unknown@example.com')
    vehicle = request.form.get('vehicle', 'Unknown Vehicle')
    code = request.form.get('code', 'N/A').upper()

    # Prompt to OpenAI
    prompt = f"""
You are an automotive diagnostic assistant. The customer submitted the OBD2 diagnostic trouble code: {code}.

Create a structured report with the following **bolded markdown labels** exactly:

**Technical Explanation:** (Short technical summary)
**Layman's Summary:** (Easy to understand version)
**Urgency (X/10):** (How important is this, from 1 to 10)
**Estimated Repair Cost in CAD:** (Reasonable range in Canadian dollars)
**Consequences of Ignoring:** (What could happen if it's not fixed)
**Preventative Tips:** (Advice to prevent it)
**DIY Potential:** (Can the average person fix this?)
**Environmental Impact:** (How this affects the environment)

Keep responses clear, brief, and formatted exactly as asked.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=700
        )
        ai_output = response['choices'][0]['message']['content']
    except Exception as e:
        ai_output = f"Error generating report: {str(e)}"

    # Parse each section from the AI response
    tech_summary         = extract_section("Technical Explanation", ai_output)
    layman_summary       = extract_section("Layman's Summary", ai_output)
    urgency_raw          = extract_section("Urgency (", ai_output)
    urgency              = urgency_raw.split("/")[0] if "/" in urgency_raw else "–"
    urgency_explanation  = urgency_raw
    repair_cost          = extract_section("Estimated Repair Cost in CAD", ai_output)
    consequences         = extract_section("Consequences of Ignoring", ai_output)
    preventative_tips    = extract_section("Preventative Tips", ai_output)
    diy_potential        = extract_section("DIY Potential", ai_output)
    environmental_impact = extract_section("Environmental Impact", ai_output)

    return render_template("report.html",
        name=name,
        vehicle=vehicle,
        code=code,
        email=email,
        urgency=urgency,
        urgency_explanation=urgency_explanation,
        tech_summary=tech_summary,
        layman_summary=layman_summary,
        repair_cost=repair_cost,
        consequences=consequences,
        preventative_tips=preventative_tips,
        diy_potential=diy_potential,
        environmental_impact=environmental_impact,
        recommended_mechanic="Clover Auto & Tecumseh Auto (Windsor)",
        video_link=f"https://www.youtube.com/results?search_query=OBD2+Code+{code}+explanation"
    )

# Required for Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
