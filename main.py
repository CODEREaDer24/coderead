import os
import openai
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/report', methods=['POST'])
def report():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        make = request.form.get('make')
        model = request.form.get('model')
        year = request.form.get('year')
        code = request.form.get('code')

        prompt = f"""
        Vehicle: {year} {make} {model}
        Trouble Code: {code}

        Provide:
        1. Technical explanation
        2. Layman's explanation
        3. Urgency level (1–10) with reasoning
        4. Estimated repair cost in CAD
        5. Consequences of ignoring it
        6. Preventative care tips
        7. DIY repair potential
        8. Environmental impact
        9. Related OBD2 codes or common companion codes
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a master-level auto diagnostics technician with a clear, confident tone."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response['choices'][0]['message']['content']

        def extract(label):
            import re
            match = re.search(f"{label}[:\\n\\r]+(.*?)(\\n\\n|$)", content, re.IGNORECASE | re.DOTALL)
            return match.group(1).strip() if match else f"{label} not found."

        # Real YouTube links (expand as needed)
        youtube_links = {
            "P0320": [
                {
                    "title": "P0320 Crankshaft Sensor Explained",
                    "url": "https://www.youtube.com/watch?v=LSxBdj3kKYI"
                },
                {
                    "title": "How to Diagnose & Fix P0320",
                    "url": "https://www.youtube.com/watch?v=9M1i6F4I6hU"
                }
            ],
            "default": [
                {
                    "title": f"OBD2 Code {code} Explanation",
                    "url": f"https://www.youtube.com/results?search_query=OBD2+code+{code}+explanation"
                }
            ]
        }

        selected_videos = youtube_links.get(code.upper(), youtube_links["default"])

        return render_template("report.html",
            name=name,
            email=email,
            phone=phone,
            make=make,
            model=model,
            year=year,
            code=code,
            urgency_gauge_url="/static/urgency_gauge_placeholder.png",
            urgency_explanation=extract("Urgency"),
            technical_explanation=extract("Technical explanation"),
            layman_explanation=extract("Layman's explanation"),
            estimated_cost=extract("Estimated repair cost").replace("$", "").replace("CAD", "").strip(),
            consequences=extract("Consequences"),
            prevention=extract("Preventative care"),
            diy=extract("DIY"),
            environment=extract("Environmental impact"),
            relationships=extract("Related OBD2 codes"),
            videos=selected_videos,
            mechanics=[
                {"name": "Clover Auto", "url": "https://www.cloverauto.ca", "rating": 4.8},
                {"name": "Tecumseh Auto Repair", "url": "https://www.tecumsehautorepair.com", "rating": 4.6},
                {"name": "Auto Clinic Windsor", "url": "https://www.google.com/search?q=auto+clinic+windsor", "rating": 4.7}
            ]
        )

    except Exception as e:
        return f"OpenAI API Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
