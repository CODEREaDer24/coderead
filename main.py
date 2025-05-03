from flask import Flask, render_template, request
import openai
import os

app = Flask(__name__)

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Form and report route
@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'GET':
        return render_template('form.html')

    name = request.form.get('name', 'Unknown')
    email = request.form.get('email', 'unknown@example.com')
    vehicle = request.form.get('vehicle', 'Unknown Vehicle')
    code = request.form.get('code', 'N/A').upper()

    try:
        prompt = (
            f"Explain automotive OBD2 code {code} in detail.\n"
            f"1. Technical explanation\n"
            f"2. Layman explanation\n"
            f"3. Urgency (1–10 and why)\n"
            f"4. Repair cost (CAD)\n"
            f"5. Consequences of ignoring\n"
            f"6. Preventative tips\n"
            f"7. DIY potential\n"
            f"8. Environmental impact\n"
            f"9. Recommended mechanic (Windsor)\n"
            f"10. YouTube video URL"
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        content = response['choices'][0]['message']['content']
        parts = content.split('\n')

        urgency_line = next((line for line in parts if line.startswith("3.")), "3. Urgency: 5 – unknown")
        urgency_val = ''.join(filter(str.isdigit, urgency_line.split(':')[1].strip().split()[0]))
        urgency = int(urgency_val) if urgency_val else 5

        return render_template('report.html',
            name=name,
            email=email,
            vehicle=vehicle,
            code=code,
            urgency=urgency,
            urgency_explanation=urgency_line.split("–", 1)[-1].strip(),
            tech_summary=parts[0].split(":", 1)[-1].strip(),
            layman_summary=parts[1].split(":", 1)[-1].strip(),
            repair_cost=parts[3].split(":", 1)[-1].strip(),
            consequences=parts[4].split(":", 1)[-1].strip(),
            preventative_tips=parts[5].split(":", 1)[-1].strip(),
            diy_potential=parts[6].split(":", 1)[-1].strip(),
            environmental_impact=parts[7].split(":", 1)[-1].strip(),
            recommended_mechanic=parts[8].split(":", 1)[-1].strip(),
            video_link=parts[9].split(":", 1)[-1].strip()
        )

    except Exception as e:
        return f"AI report generation failed: {e}"

# Run app locally or on Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
