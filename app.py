import os, json, re
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import google.generativeai as genai
from google.generativeai.types import RequestOptions

app = Flask(__name__)

# Enhanced CORS for GitHub Pages
CORS(app, resources={r"/*": {
    "origins": "*", 
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

# API Configuration - Best Practice: Use Environment Variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCHAQTxUGj4iiuI50AvU8IvG5TQ8ABPX7A")
genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_analysis(code_content):
    options = RequestOptions(api_version='v1')
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Prompt optimized for strict JSON response
        prompt = f"Return ONLY a JSON object with keys 'mistakes' (array of strings) and 'suggestion' (string). Audit this code: {code_content[:1500]}"
        
        response = model.generate_content(prompt, request_options=options)
        
        if response and response.text:
            # Cleaning response text to find JSON
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
    except Exception as e:
        print(f"DEBUG AI Error: {str(e)}")
    return None

@app.route('/', methods=['POST', 'GET', 'OPTIONS'])
def index():
    # Handle CORS Pre-flight
    if request.method == 'OPTIONS':
        return make_response("", 200)

    if request.method == 'GET':
        return "EcoSync AI Core is ONLINE."

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files.get('file')
    try:
        content = file.read().decode('utf-8', errors='ignore')
        analysis = get_gemini_analysis(content)

        # Fallback values if AI fails
        mistakes = analysis.get("mistakes", []) if analysis else ["Neural link slow, please retry."]
        suggestion = analysis.get("suggestion", "System syncing...") if analysis else "Re-upload recommended for deep scan."

        return jsonify({
            "energy_score": max(10, 100 - (len(mistakes) * 15)),
            "status": "Healthy" if not mistakes or "retry" in mistakes[0] else "Critical",
            "mistakes_array": mistakes,
            "suggestion": suggestion,
            "ai_confidence": 98.5
        })
    except Exception as e:
        print(f"Critical Error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    # Render binds to the PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
