import os
import json
from flask import Flask, render_template, request, redirect, url_for
import openai

app = Flask(__name__)

# Set your OpenAI API key in an environment variable for safety.
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def index():
    # Render the homepage with the diagnostic form.
    return render_template("index.html")

@app.route("/report", methods=["POST"])
def report():
    # Collect form data from the request.
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    make = request.form.get("make", "").strip()
    model = request.form.get("model", "").strip()
    year = request.form.get("year", "").strip()
    code = request.form.get("code", "").strip()

    # Basic validation: ensure all fields are provided.
    if not all([name, email, phone, make, model, year, code]):
        # If any field is missing, redirect back to the homepage.
        return redirect(url_for("index"))

    # Prepare the OpenAI API prompt/messages for GPT-4.
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert automotive technician AI. "
                "Provide concise car diagnostic information in JSON format."
            )
        },
        {
            "role": "user",
            "content": (
                f"My vehicle is a {year} {make} {model} with the code {code}. "
                "Provide a JSON diagnostic report with keys: explanation, urgency, estimated_cost, video_links. "
                "Respond only with a JSON object."
            )
        }
    ]

    result = {}
    try:
        # Call the OpenAI API (GPT-4) to get a completion.
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0  # use deterministic output for consistent JSON
        )
        # Parse the JSON response from the AI.
        reply_content = response.choices[0].message.content
        result = json.loads(reply_content)
    except Exception as e:
        # If the API call fails or returns invalid JSON, use fallback defaults.
        result = {}

    # Define fallback default values for the report fields.
    fallback = {
        "explanation": "No explanation is available for this code.",
        "urgency": "Unknown",
        "estimated_cost": "N/A",
        "video_links": []
    }
    # Ensure all expected keys exist in the result; fill missing ones with defaults.
    for key, default_value in fallback.items():
        if key not in result or result[key] is None or result[key] == "":
            result[key] = default_value

    # Validate and filter video link URLs (ensure they start with http:// or https://).
    links = result.get("video_links", [])
    if not isinstance(links, list):
        links = [links] if links else []
    valid_links = []
    for link in links:
        if isinstance(link, str) and link.startswith(("http://", "https://")):
            valid_links.append(link)
    result["video_links"] = valid_links

    # Render the report page with the data (use the template to format nicely).
    return render_template(
        "report.html",
        name=name,
        email=email,
        phone=phone,
        make=make,
        model=model,
        year=year,
        code=code,
        explanation=result["explanation"],
        urgency=result["urgency"],
        estimated_cost=result["estimated_cost"],
        video_links=result["video_links"]
    )

# Run the Flask app (for local testing or if not using a separate WSGI server).
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
