import os, json, re
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import google.generativeai as genai
from google.generativeai.types import RequestOptions

app = Flask(__name__)
CORS(app)

# API Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCHAQTxUGj4iiuI50AvU8IvG5TQ8ABPX7A")
genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_analysis(code_content):
    # FORCE API VERSION TO V1 (Important!)
    # Is se v1beta wala 404 error khatam ho jayega
    options = RequestOptions(api_version='v1')
    
    # Models to try
    models = ['gemini-1.5-flash', 'gemini-pro']
    
    for m_id in models:
        try:
            print(f"DEBUG: Connecting to {m_id} using API v1...")
            model = genai.GenerativeModel(m_id)
            
            prompt = f"Return ONLY JSON: {{'mistakes': [], 'suggestion': ''}}. Audit: {code_content[:1000]}"
            
            # Requesting with explicit v1 options
            response = model.generate_content(prompt, request_options=options)
            
            if response and response.text:
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match:
                    print(f"SUCCESS: {m_id} is working!")
                    return json.loads(match.group(0))
        except Exception as e:
            print(f"DEBUG: {m_id} failed: {str(e)}")
            continue
    return None

@app.route('/', methods=['POST', 'GET', 'OPTIONS'])
def index():
    if request.method == 'OPTIONS': return make_response("", 200)
    if request.method == 'GET': return "EcoSync AI Core is ONLINE (v1 Force)."

    file = request.files.get('file')
    if not file: return jsonify({"error": "No file"}), 400

    try:
        content = file.read().decode('utf-8', errors='ignore')
        analysis = get_gemini_analysis(content)

        if not analysis:
            return jsonify({
                "energy_score": 0,
                "status": "AI_OFFLINE",
                "mistakes_array": ["API Version Mismatch. Still getting 404."],
                "suggestion": "Please check if 'google-generativeai' version in requirements.txt is latest."
            })

        return jsonify({
            "energy_score": max(10, 100 - (len(analysis.get("mistakes", [])) * 15)),
            "status": "Healthy" if not analysis.get("mistakes") else "Critical",
            "mistakes_array": analysis.get("mistakes", []),
            "suggestion": analysis.get("suggestion", "System synced."),
            "ai_confidence": 98.5
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
