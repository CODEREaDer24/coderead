import os
import openai
from flask import Flask, render_template, request, render_template_string
from dotenv import load_dotenv

# Load environment variables (useful locally)
load_dotenv()

# Set OpenAI key from Render or .env
openai.api_key = os.getenv("OPENAI_API_KEY")

# Start Flask app
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

        # Prompt to OpenAI
        prompt = f"""
        You're a car diagnostic assistant. A customer has a {year} {make} {model} with trouble code {code}.
        Explain what this code means in simple terms. Include urgency level, possible causes, repair cost,
        consequences of ignoring it, and any tips for DIY or prevention.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # <<— downgraded model here
            messages=[
                {"role": "system", "content": "You are an expert automotive diagnostic assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        result = response['choices'][0]['message']['content']

        return render_template_string("""
            <h1>CodeREAD Diagnostic Report</h1>
            <p><strong>Name:</strong> {{ name }}</p>
            <p><strong>Vehicle:</strong> {{ year }} {{ make }} {{ model }}</p>
            <p><strong>Diagnostic Code:</strong> {{ code }}</p>
            <hr>
            <pre>{{ result }}</pre>
        """, name=name, year=year, make=make, model=model, code=code, result=result)

    except Exception as e:
        print("OpenAI API Error:", e)
        return render_template_string("""
            <h1>Error</h1>
            <p>OpenAI failed to generate a response. Please check your API key or try again later.</p>
            <p>{{ error }}</p>
        """, error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
