import os, json, re
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# API Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCHAQTxUGj4iiuI50AvU8IvG5TQ8ABPX7A")
genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_analysis(code_content):
    # Try multiple model variants in case of 404
    for model_id in ['gemini-1.5-flash', 'gemini-pro']:
        try:
            print(f"DEBUG: Attempting to connect to {model_id}...")
            model = genai.GenerativeModel(model_id)
            
            prompt = f"Return ONLY JSON: {{'mistakes': [], 'suggestion': ''}}. Audit: {code_content[:1000]}"
            response = model.generate_content(prompt)
            
            if response and response.text:
                # Find JSON in response
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match:
                    print(f"SUCCESS: Connected to {model_id}")
                    return json.loads(match.group(0))
        except Exception as e:
            print(f"DEBUG: {model_id} failed with error: {str(e)}")
            continue # Try the next model
    return None

@app.route('/', methods=['POST', 'GET', 'OPTIONS'])
def index():
    if request.method == 'OPTIONS':
        return make_response("", 200)

    if request.method == 'GET':
        return "EcoSync AI Core is ONLINE."

    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files.get('file')
    try:
        content = file.read().decode('utf-8', errors='ignore')
        analysis = get_gemini_analysis(content)

        # Logical checks for Frontend
        if not analysis:
            return jsonify({
                "energy_score": 0,
                "status": "AI_OFFLINE",
                "mistakes_array": ["Model Connection Error (404)."],
                "suggestion": "Google AI is rejecting the model request. Check API Key permissions.",
                "ai_confidence": 0
            })

        mistakes = analysis.get("mistakes", [])
        return jsonify({
            "energy_score": max(10, 100 - (len(mistakes) * 15)),
            "status": "Healthy" if not mistakes else "Critical",
            "mistakes_array": mistakes,
            "suggestion": analysis.get("suggestion", "System syncing..."),
            "ai_confidence": 98.5
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
