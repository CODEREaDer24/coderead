from flask import Flask, request, render_template_string
import urllib.parse

app = Flask(__name__)

# Register the urlencode filter
@app.template_filter('urlencode')
def urlencode_filter(s):
    return urllib.parse.quote_plus(s)

# Fake mechanic data
mechanics = [
    {
        "name": "DLH Auto Service",
        "address": "2378 Central Ave, Windsor, ON",
        "maps": "https://maps.google.com/?q=2378+Central+Ave+Windsor+ON"
    },
    {
        "name": "Demario’s Auto Clinic",
        "address": "2366 Dougall Ave, Windsor, ON",
        "maps": "https://maps.google.com/?q=2366+Dougall+Ave+Windsor+ON"
    },
    {
        "name": "Kipping Tire & Automotive",
        "address": "1197 Ouellette Ave, Windsor, ON",
        "maps": "https://maps.google.com/?q=1197+Ouellette+Ave+Windsor+ON"
    }
]

# HTML template for form
FORM_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>CodeREAD Form</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" />
  <style>
    body { background-color: #111; color: #fff; font-family: Arial, sans-serif; }
    .form-box { max-width: 500px; margin: auto; margin-top: 3rem; background-color: #222; padding: 2rem; border-radius: 1rem; }
    .btn-warning { width: 100%; }
  </style>
</head>
<body>
  <div class="form-box">
    <h2 class="text-center text-warning">CodeREAD Diagnostic</h2>
    <form action="/submit" method="POST">
      <div class="mb-3">
        <label class="form-label">Your Name</label>
        <input type="text" name="name" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input type="email" name="email" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">OBD-II Code</label>
        <input type="text" name="code" class="form-control" required />
      </div>
      <button type="submit" class="btn btn-warning">Generate Report</button>
    </form>
  </div>
</body>
</html>
"""

# HTML template for report
REPORT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>CodeREAD Report</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" />
  <style>
    body { background-color: #1a1a1a; color: #f1f1f1; font-family: 'Segoe UI', sans-serif; }
    .report-box { background-color: #222; padding: 2rem; border-radius: 1rem; box-shadow: 0 0 15px #000; max-width: 700px; margin: auto; }
    .urgency-meter { margin-top: 1rem; }
    .brand { font-size: 2rem; font-weight: bold; color: #ffc107; text-align: center; margin-bottom: 1rem; }
    .link-yellow { color: #ffc107; text-decoration: underline; }
  </style>
</head>
<body class="py-5">

  <div class="brand">CodeREAD</div>

  <div class="report-box">
    <h4>OBD-II Code: <span class="text-warning">{{ code }}</span></h4>
    <p><strong>Urgency Level:</strong> {{ urgency }} MPH</p>

    <div class="urgency-meter">
      <div class="progress">
        <div class="progress-bar bg-warning" role="progressbar" style="width: {{ urgency }}%;" aria-valuenow="{{ urgency }}" aria-valuemin="0" aria-valuemax="100"></div>
      </div>
    </div>

    <hr />

    <h5>AI-Generated Advice</h5>
    <p>{{ advice }}</p>

    <hr />

    <h5>Recommended Windsor Mechanics</h5>
    <ul>
      {% for mech in mechanics %}
        <li>
          <strong>{{ mech.name }}</strong><br />
          <a class="link-yellow" href="{{ mech.maps }}" target="_blank">{{ mech.address }}</a>
        </li>
      {% endfor %}
    </ul>

    <hr />

    <h5>Helpful Video</h5>
    <a class="link-yellow" href="https://www.youtube.com/results?search_query={{ code | urlencode }}" target="_blank">
      Search "{{ code }}" on YouTube
    </a>
  </div>

</body>
</html>
"""

# Sample logic for urgency + advice
def get_advice_for_code(code):
    code = code.upper().strip()
    if code.startswith("P03"):
        return 85, "Engine misfire detected. Avoid driving long distances — get it checked soon."
    elif code.startswith("P04"):
        return 60, "Emissions issue. May affect fuel economy but not urgent."
    elif code.startswith("P01"):
        return 95, "Fuel system fault. Immediate attention recommended."
    else:
        return 45, "General engine code. Safe to drive short term."

# Route: show form
@app.route("/")
def form():
    return render_template_string(FORM_HTML)

# Route: handle form submission
@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    email = request.form.get("email")
    code = request.form.get("code", "").strip().upper()
    urgency, advice = get_advice_for_code(code)

    return render_template_string(REPORT_HTML,
                                  code=code,
                                  urgency=urgency,
                                  advice=advice,
                                  mechanics=mechanics)

if __name__ == "__main__":
    app.run(debug=True)
