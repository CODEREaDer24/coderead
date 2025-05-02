from flask import Flask, request, render_template_string
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

form_html = """
<!DOCTYPE html>
<html>
<head><title>CodeREAD Diagnostic</title></head>
<body style="font-family:sans-serif; padding:40px;">
  <h2>CodeREAD Diagnostic Report Generator</h2>
  <form method="POST">
    <label>Customer Name:</label><br>
    <input name="name"><br><br>
    <label>Vehicle (make/model/year):</label><br>
    <input name="vehicle"><br><br>
    <label>OBD2 Code:</label><br>
    <input name="code"><br><br>
    <label>Email:</label><br>
    <input name="email"><br><br>
    <button type="submit">Generate Report</button>
  </form>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def generate_report():
    if request.method == 'POST':
        name = request.form.get('name')
        vehicle = request.form.get('vehicle')
        code = request.form.get('code')
        email = request.form.get('email')

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a vehicle diagnostics expert."},
                    {"role": "user", "content": f"Generate a diagnostic report for code {code} on a {vehicle}."}
                ]
            )
            analysis = response['choices'][0]['message']['content']
        except Exception as e:
            analysis = f"Error generating analysis: {str(e)}"

        return f"""
        <pre>
        CodeREAD Vehicle Diagnostic Report
        ----------------------------------
        Customer Name: {name}
        Vehicle: {vehicle}
        OBD2 Code: {code}
        Email: {email}

        AI Diagnostic Analysis:
        {analysis}
        </pre>
        """

    return form_htmlp
