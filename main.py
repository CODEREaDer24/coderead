from flask import Flask, render_template, request
import os
import openai

app = Flask(__name__)

# Load your OpenAI API key from environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Homepage with diagnostic form
@app.route('/')
def index():
    return render_template('form.html')

# Generate route — calls OpenAI and builds the report
@app.route('/generate', methods=['POST'])
def generate():
    name = request.form.get('name', 'Unknown')
    email = request.form.get('email', 'unknown@example.com')
    vehicle = request.form.get('vehicle', 'Unknown Vehicle')
    code = request.form.get('code', 'N/A').upper()

    # Prompt sent to OpenAI
    prompt = f"""
You are an automotive diagnostic assistant. The customer has entered the diagnostic trouble code: {code}.

Create a structured report including:
- A brief technical explanation
- A simplified layman's summary
- Urgency (scale 1–10) with explanation
- Estimated repair cost in CAD
- Consequences of ignoring
- Preventative tips
- DIY potential
- Environmental impact

Make the tone professional but clear. Keep answers concise and easy to read.
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

    # For now, just dump the output into the 'tech_summary' field for testing
    return render_template("report.html",
        name=name,
        vehicle=vehicle,
        code=code,
        email=email,
        urgency="–",
        urgency_explanation="–",
        tech_summary=ai_output,
        layman_summary="–",
        repair_cost="–",
        consequences="–",
        preventative_tips="–",
        diy_potential="–",
        environmental_impact="–",
        recommended_mechanic="Clover Auto & Tecumseh Auto (Windsor)",
        video_link=f"https://www.youtube.com/results?search_query=OBD2+Code+{code}+explanation"
    )

# Render-compatible run block
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
