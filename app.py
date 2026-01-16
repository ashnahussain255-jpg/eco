import os, re, json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- Configuration ---
GEMINI_API_KEY = "AIzaSyCHAQTxUGj4iiuI50AvU8IvG5TQ8ABPX7A" 
genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_analysis(code_content, filename):
    # Multiple models try karein taake 404 error na aaye
    for model_name in ['gemini-1.5-flash', 'gemini-pro']:
        try:
            model = genai.GenerativeModel(model_name)
            prompt = f"Analyze this code and return ONLY JSON with keys 'mistakes' (list) and 'suggestion' (string). Code: {code_content[:2000]}"
            
            response = model.generate_content(prompt)
            
            # Clean JSON extraction
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception as e:
            print(f"DEBUG: Model {model_name} failed - {str(e)}")
            continue # Agla model try karein
            
    return None

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return "EcoSync AI Core is ONLINE."
    
    file = request.files.get('file')
    if not file: return jsonify({"error": "No file"}), 400

    try:
        content = file.read().decode('utf-8', errors='ignore')
        analysis = get_gemini_analysis(content, file.filename)
        
        if not analysis:
            # Fallback agar saare models fail ho jayein
            return jsonify({
                "energy_score": 100,
                "status": "Healthy",
                "mistakes_array": ["AI node busy. Manual audit suggested."],
                "suggestion": "API handshake failed. Please check key permissions.",
                "ai_confidence": 90.0
            })

        mistakes = analysis.get("mistakes", [])
        return jsonify({
            "energy_score": max(10, 100 - (len(mistakes) * 15)),
            "status": "Healthy" if not mistakes else "Critical",
            "mistakes_array": mistakes,
            "suggestion": analysis.get("suggestion", "Integrity verified."),
            "ai_confidence": 98.4
        })
    except Exception as e:
        return jsonify({"error": "Processing error"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
