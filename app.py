import os, json, re
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# API Key - Free Tier
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCHAQTxUGj4iiuI50AvU8IvG5TQ8ABPX7A")
genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_analysis(code_content):
    # Free Tier mein ye 2 models best chaltay hain
    # Humne 'models/' prefix add kar diya hai taake 404 na aaye
    for model_name in ['models/gemini-1.5-flash', 'models/gemini-pro']:
        try:
            print(f"DEBUG: Connecting to {model_name}...")
            model = genai.GenerativeModel(model_name)
            
            prompt = f"Return ONLY JSON: {{'mistakes': [], 'suggestion': ''}}. Audit: {code_content[:1000]}"
            response = model.generate_content(prompt)
            
            if response and response.text:
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match:
                    print(f"SUCCESS: Connected via {model_name}")
                    return json.loads(match.group(0))
        except Exception as e:
            print(f"DEBUG: {model_name} failed: {str(e)}")
            continue
    return None

@app.route('/', methods=['POST', 'GET', 'OPTIONS'])
def index():
    if request.method == 'OPTIONS': return make_response("", 200)
    if request.method == 'GET': return "EcoSync Free Tier Core is ONLINE."

    file = request.files.get('file')
    if not file: return jsonify({"error": "No file"}), 400

    try:
        content = file.read().decode('utf-8', errors='ignore')
        analysis = get_gemini_analysis(content)

        if not analysis:
            return jsonify({
                "energy_score": 50,
                "status": "AI_LIMIT",
                "mistakes_array": ["Free tier quota or model access issue."],
                "suggestion": "Check if your API Key is active in Google AI Studio."
            })

        return jsonify({
            "energy_score": max(10, 100 - (len(analysis.get("mistakes", [])) * 15)),
            "status": "Healthy" if not analysis.get("mistakes") else "Critical",
            "mistakes_array": analysis.get("mistakes", []),
            "suggestion": analysis.get("suggestion", "Keep coding!"),
            "ai_confidence": 98.5
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
