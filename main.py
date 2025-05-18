 import os
Email: {email}
Phone: {phone}
Address: {address}
Vehicle: {vehicle_year} {vehicle_make} {vehicle_model}
Diagnostic Code(s): {diagnostic_codes}

For each code, include:
- Technical Explanation
- Layman’s Explanation
- Urgency (1–10)
- Estimated Repair Cost (CAD)
- Consequences of Not Fixing
- Preventative Tips
- DIY Potential
- Environmental Impact
- Video link for explanation or DIY repair
- CodeREAD AI Recommendation (DIY or see mechanic)

Then provide 3 Windsor-based mechanic shop recommendations with contact info.
"""

    try:
        logging.info("Sending prompt to OpenAI...")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a car diagnostics expert writing CodeREAD reports."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        report_text = response['choices'][0]['message']['content']
        last_report_text = report_text  # store for preview

        # Save cleaned version as PDF
        cleaned_text = report_text.encode('ascii', 'ignore').decode('ascii')
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        pdf.set_fill_color(0, 0, 0)
        pdf.set_text_color(255, 255, 0)
        pdf.cell(200, 10, txt="CodeREAD Diagnostic Report", ln=True, align='C', fill=True)
        pdf.ln(5)

        pdf.set_text_color(255, 255, 255)
        intro = f"""
Customer: {name}
Email: {email}
Phone: {phone}
Address: {address}
Vehicle: {vehicle_year} {vehicle_make} {vehicle_model}
Diagnostic Code(s): {diagnostic_codes}
"""
        pdf.multi_cell(0, 10, intro)
        pdf.ln(2)
        pdf.multi_cell(0, 10, cleaned_text)

        _, tmp_path = tempfile.mkstemp(suffix=".pdf")
        pdf.output(tmp_path)
        last_pdf_path = tmp_path

    except Exception as e:
        logging.error(f"GPT error: {e}")
        return "Error generating report. Please try again later."

    return render_template("report.html", report_text=report_text)

@app.route('/download')
def download():
    global last_pdf_path
    if last_pdf_path and os.path.exists(last_pdf_path):
        return send_file(last_pdf_path, as_attachment=True, download_name="CodeREAD_Report.pdf")
    return "No PDF found."
