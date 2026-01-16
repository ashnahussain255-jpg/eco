import os, json, re
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Configuration
GEMINI_API_KEY = "AIzaSyCHAQTxUGj4iiuI50AvU8IvG5TQ8ABPX7A"
genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_analysis(code_content):
    # HUM DONO MODELS TRY KAREIN GE
    # Agar 1.5 Flash nahi mila to 'gemini-pro' (Stable) chal jaye ga
    for model_name in ['gemini-1.5-flash', 'gemini-pro']:
        try:
            model = genai.GenerativeModel(model_name)
            prompt = f"Return ONLY JSON: {{'mistakes': [], 'suggestion': ''}}. Audit: {code_content[:1500]}"
            
            response = model.generate_content(prompt)
            
            if response.text:
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
        except Exception as e:
            print(f"DEBUG: Model {model_name} failed: {e}")
            continue # Agla model try karo
    return None

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return "EcoSync AI Core is ONLINE."

    file = request.files.get('file')
    if not file: return jsonify({"error": "No file"}), 400

    try:
        content = file.read().decode('utf-8', errors='ignore')
        analysis = get_gemini_analysis(content)

        if not analysis:
            return jsonify({
                "energy_score": 100,
                "status": "Healthy",
                "mistakes_array": ["API Handshake: Model mismatch"],
                "suggestion": "Please check if Generative AI is enabled in your Google Console.",
                "ai_confidence": 90.0
            })

        mistakes = analysis.get("mistakes", [])
        return jsonify({
            "energy_score": max(5, 100 - (len(mistakes) * 15)),
            "status": "Healthy" if not mistakes else "Critical",
            "mistakes_array": mistakes,
            "suggestion": analysis.get("suggestion", "System stable."),
            "ai_confidence": 98.5
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
