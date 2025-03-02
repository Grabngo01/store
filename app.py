from flask import Flask, render_template, request, jsonify
import requests
import sys
import os

app = Flask(__name__, template_folder="templates")

# Google Apps Script Web App URL
GOOGLE_SHEETS_API_URL = "https://script.google.com/macros/s/AKfycbyDXtAjAckROA54r48-_HWOTpacHnCskuVflG5FIOlTQzqJQ6U9SVBF1zOfhQMtc1W0eQ/exec"

@app.route('/')
def index():
    return render_template('index.html')

# Fetch Data from Google Sheets
def fetch_data(sheet_name):
    try:
        response = requests.get(f"{GOOGLE_SHEETS_API_URL}?sheet={sheet_name}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        print(f"Timeout error fetching {sheet_name} data", file=sys.stderr)
        return {"error": "Request timed out"}
    except requests.RequestException as e:
        print(f"Error fetching {sheet_name} data: {e}", file=sys.stderr)
        return {"error": "Failed to fetch data"}

@app.route('/data')
def get_data():
    return jsonify({
        "employee_hours": fetch_data("Employee_Hours"),
        "expenses": fetch_data("Expenses"),
        "revenue": fetch_data("Revenue")
    })

# Submit Data to Google Sheets
@app.route('/submit', methods=['POST'])
def submit_data():
    data = request.json
    sheet_name = data.get("sheet")
    values = data.get("values")
    
    if not sheet_name or not values:
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        response = requests.post(f"{GOOGLE_SHEETS_API_URL}?sheet={sheet_name}", json=values, timeout=10)
        response.raise_for_status()
        return jsonify({"message": "Data submitted successfully"})
    except requests.Timeout:
        print(f"Timeout error submitting data to {sheet_name}", file=sys.stderr)
        return jsonify({"error": "Request timed out"}), 500
    except requests.RequestException as e:
        print(f"Error submitting data: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to submit data"}), 500

if __name__ == '__main__':
    try:
        print("Starting Flask app on 0.0.0.0:8080")
        app.run(debug=True, host="0.0.0.0", port=8080)
    except Exception as e:
        print(f"Flask app failed to start: {e}", file=sys.stderr)
        sys.exit(1)
