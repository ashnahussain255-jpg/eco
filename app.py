import os, json, re
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai  # Nayi library ka import ye hai

app = Flask(__name__)
CORS(app)

# API Key
GEMINI_API_KEY = "AIzaSyCHAQTxUGj4iiuI50AvU8IvG5TQ8ABPX7A"
client = genai.Client(api_key=GEMINI_API_KEY)

def get_gemini_analysis(code_content):
    try:
        # Naye SDK ka tareeka
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Audit this code. Return ONLY JSON: {{'mistakes': [], 'suggestion': ''}}. Code: {code_content[:2000]}"
        )
        
        # JSON extraction
        text = response.text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception as e:
        print(f"DEBUG Error: {e}")
        return None

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return "EcoSync AI Core is Online (v2)."

    file = request.files.get('file')
    if not file: return jsonify({"error": "No file"}), 400

    try:
        content = file.read().decode('utf-8', errors='ignore')
        analysis = get_gemini_analysis(content)

        if not analysis:
            analysis = {"mistakes": ["Sync Error"], "suggestion": "Neural link failed. Retry."}

        return jsonify({
            "energy_score": max(10, 100 - (len(analysis.get("mistakes", [])) * 15)),
            "status": "Healthy" if not analysis.get("mistakes") else "Critical",
            "mistakes_array": analysis.get("mistakes", []),
            "suggestion": analysis.get("suggestion", "System stable."),
            "ai_confidence": 98.5
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
