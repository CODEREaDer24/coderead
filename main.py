<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CodeREAD Diagnostic Form</title>
    <style>
        body {
            background-color: #000;
            color: #FFD700;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 700px;
            margin: 40px auto;
            padding: 20px;
            background-color: #111;
            border-radius: 10px;
            box-shadow: 0 0 20px #FFD700;
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            color: #FFD700;
        }
        label {
            display: block;
            margin: 15px 0 5px;
        }
        input, textarea {
            width: 100%;
            padding: 10px;
            background: #222;
            color: #FFD700;
            border: 1px solid #FFD700;
            border-radius: 5px;
        }
        input:required, textarea:required {
            border-color: #FF4500;
        }
        button {
            display: block;
            width: 100%;
            padding: 15px;
            margin-top: 30px;
            background-color: #FFD700;
            color: #000;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #FFA500;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            font-size: 14px;
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>CodeREAD Diagnostic Form</h1>
        <form action="/report" method="post">
            <label for="name">Customer Name *</label>
            <input type="text" id="name" name="name" required>

            <label for="email">Email Address *</label>
            <input type="email" id="email" name="email" required>

            <label for="phone">Phone Number *</label>
            <input type="tel" id="phone" name="phone" required>

            <label for="address">Address (optional)</label>
            <input type="text" id="address" name="address">

            <label for="vehicle_make">Vehicle Make *</label>
            <input type="text" id="vehicle_make" name="vehicle_make" required>

            <label for="vehicle_model">Vehicle Model *</label>
            <input type="text" id="vehicle_model" name="vehicle_model" required>

            <label for="vehicle_year">Vehicle Year *</label>
            <input type="number" id="vehicle_year" name="vehicle_year" min="1900" max="2099" required>

            <label for="codes">Diagnostic Trouble Code(s) *</label>
            <textarea id="codes" name="codes" rows="4" placeholder="Enter one or more OBD-II codes (e.g., P0171, P0455)" required></textarea>

            <button type="submit">Auto-Generate Report</button>
        </form>
        <div class="footer">
            &copy; 2025 CodeREAD.ca — AI Diagnostics That Drive Trust.
        </div>
    </div>
</body>
</html>
