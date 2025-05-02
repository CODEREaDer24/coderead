from flask import Flask, request, render_template_string
import openai
import os

app = Flask(__name__)

# Load API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# HTML form (for testing)
html_form = '''
<!doctype html>
<html>
<head><title>CodeREAD Report Generator</title></head>
<body style="font-family: sans-serif;">
  <h2>Enter Diagnostic Info</h2>
  <form method="POST">
    Customer Name: <input name="name"><br><br>
    Vehicle Info: <input name="vehicle"><br><br>
    OBD2 Code: <input name="code"><br><br>
    Email: <input name="email"><br><br>
    <button type="submit">Generate Report</button>
  </form>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def generate_report():
    if request.method == 'POST':
        name = request.form['name']
        vehicle = request.form['vehicle']
        code = request.form['code']
        email = request.form['email']

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a diagnostic expert generating detailed vehicle issue reports for customers."},
                    {"role": "user", "content": f"Generate a CodeREAD report for code {code} on a {vehicle}."}
                ]
            )
            analysis = response['choices'][0]['message']['content']
        except Exception as e:
            analysis = f"Error generating analysis: {str(e)}"

        report = f"""
        CodeREAD Vehicle Diagnostic Report
        ----------------------------------
        Customer Name: {name}
        Vehicle: {vehicle}
        OBD2 Code: {code}
        Email: {email}

        AI Diagnostic Analysis:
        {analysis}
        """

        return f"<pre>{report}</pre>"

    return html_form

# Run the app (for local dev)
if __name__ == "__main__":
    app.run(debug=True)
