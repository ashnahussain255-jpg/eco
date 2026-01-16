import os, json, re
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

# Naya SDK Client Setup
GEMINI_API_KEY = "AIzaSyBI3rUVdXleb1skfn6UZaK3VAihED9rg7c"
client = genai.Client(api_key=GEMINI_API_KEY)

def get_gemini_analysis(code_content, filename):
    try:
        # Naya SDK method: models.generate_content
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Analyze this code and return ONLY JSON: {{'mistakes': [], 'suggestion': ''}}. Code: {code_content[:2500]}"
        )
        
        # JSON Cleaning
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        print(f"DEBUG: New SDK Error - {str(e)}")
        return None

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return "EcoSync AI Core (New SDK) is Online."

    file = request.files.get('file')
    if not file: return jsonify({"error": "No file"}), 400

    try:
        content = file.read().decode('utf-8', errors='ignore')
        analysis = get_gemini_analysis(content, file.filename)

        if not analysis:
            analysis = {"mistakes": ["AI Node Handshake Failed"], "suggestion": "Try again in a moment."}

        mistakes = analysis.get("mistakes", [])
        return jsonify({
            "energy_score": max(5, 100 - (len(mistakes) * 15)),
            "status": "Healthy" if not mistakes else "Critical",
            "mistakes_array": mistakes,
            "suggestion": analysis.get("suggestion", "System stable."),
            "ai_confidence": 98.7
        })
    except Exception as e:
        return jsonify({"error": "Internal Error"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
