from flask import Flask, request, render_template_string

app = Flask(__name__)

FORM_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>CodeREAD Form</title>
  <style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #121212; color: #eee; }
    .container { max-width: 600px; margin: 40px auto; padding: 20px; background: #1e1e1e; border-radius: 8px; box-shadow: 0 0 15px #ffcc00; }
    label { display: block; margin-top: 15px; font-weight: bold; }
    input[type=text], input[type=email] {
      width: 100%; padding: 10px; margin-top: 6px; border: none; border-radius: 4px; background: #333; color: #eee;
    }
    button {
      margin-top: 20px; background: #ffcc00; border: none; padding: 12px 20px; font-weight: bold; color: #121212; border-radius: 4px;
      cursor: pointer; transition: background 0.3s ease;
    }
    button:hover { background: #e6b800; }
  </style>
</head>
<body>
  <div class="container">
    <h1>CodeREAD Diagnostic Form</h1>
    <form method="POST" action="/submit">
      <label for="name">Name *</label>
      <input id="name" name="name" type="text" placeholder="Jane Doe" required />
      <label for="email">Email *</label>
      <input id="email" name="email" type="email" placeholder="jane@example.com" required />
      <label for="code">Engine Code *</label>
      <input id="code" name="code" type="text" placeholder="P0420" required />
      <label for="phone">Phone</label>
      <input id="phone" name="phone" type="text" placeholder="(555) 123-4567" />
      <button type="submit">Generate Report</button>
    </form>
  </div>
</body>
</html>
"""

REPORT_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>CodeREAD Report for {{ name }}</title>
  <style>
    body {
      background: #121212;
      color: #eee;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      max-width: 700px;
      margin: 40px auto;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 0 25px #ffcc00;
      background-image: linear-gradient(135deg, #1e1e1e 25%, #292929 75%);
    }
    h1 {
      color: #ffcc00;
      border-bottom: 2px solid #ffcc00;
      padding-bottom: 10px;
      margin-bottom: 30px;
    }
    .field-label {
      font-weight: 700;
      color: #f5d94e;
    }
    .report-section {
      margin-bottom: 25px;
      padding-bottom: 15px;
      border-bottom: 1px solid #444;
    }
    a.code-link {
      color: #ffcc00;
      font-weight: bold;
      text-decoration: none;
      border-bottom: 1px dotted #ffcc00;
    }
    a.code-link:hover {
      color: #ffd633;
      border-bottom: 1px solid #ffd633;
    }
  </style>
</head>
<body>
  <h1>CodeREAD Diagnostic Report</h1>

  <div class="report-section">
    <span class="field-label">Name:</span> {{ name }}
  </div>
  <div class="report-section">
    <span class="field-label">Email:</span> {{ email }}
  </div>
  <div class="report-section">
    <span class="field-label">Phone:</span> {{ phone if phone else "N/A" }}
  </div>
  <div class="report-section">
    <span class="field-label">Engine Code:</span> 
    <a href="https://www.youtube.com/results?search_query={{ code | url_encode }}" target="_blank" class="code-link">{{ code }}</a>
  </div>

  <div class="report-section">
    <h2>Analysis</h2>
    <p>Your code <strong>{{ code }}</strong> typically indicates an issue related to the vehicle's emission system. For more info, check out the linked YouTube videos above.</p>
    <p>Contact us at <a href="mailto:support@read.codes" style="color:#ffcc00;">support@read.codes</a> for detailed diagnostics and repair advice.</p>
  </div>
</body>
</html>
"""

from flask import render_template_string
import urllib.parse

@app.route('/', methods=['GET'])
def form():
    return FORM_HTML

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    code = request.form.get('code')
    phone = request.form.get('phone')

    # Just render the report page with values and clickable link
    # Use Jinja2 render_template_string with URL encoding for the code link
    return render_template_string(
        REPORT_HTML_TEMPLATE,
        name=name,
        email=email,
        code=code,
        phone=phone
    )

if __name__ == '__main__':
    app.run(debug=True)
