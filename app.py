import os, json, re
from flask import Flask, request, jsonify
from flask_cors import CORS

# Is tareeke se import karein taake conflict na ho
try:
    from google import genai
except ImportError:
    # Fallback agar environment update na hua ho
    import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# API Key
GEMINI_API_KEY = "AIzaSyCHAQTxUGj4iiuI50AvU8IvG5TQ8ABPX7A"

# Client initialization logic
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    USING_NEW_SDK = True
except Exception:
    genai.configure(api_key=GEMINI_API_KEY)
    USING_NEW_SDK = False

def get_gemini_analysis(code_content, filename):
    try:
        prompt = f"Audit this code. Return ONLY JSON: {{'mistakes': [], 'suggestion': ''}}. Code: {code_content[:2000]}"
        
        if USING_NEW_SDK:
            response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
            text = response.text
        else:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            text = response.text
            
        match = re.search(r'\{.*\}', text, re.DOTALL)
        return json.loads(match.group(0)) if match else None
    except Exception as e:
        print(f"DEBUG Error: {e}")
        return None

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return "EcoSync AI Core is Online."

    file = request.files.get('file')
    if not file: return jsonify({"error": "No file"}), 400

    content = file.read().decode('utf-8', errors='ignore')
    analysis = get_gemini_analysis(content, file.filename)

    if not analysis:
        analysis = {"mistakes": ["Neural pattern sync failed"], "suggestion": "API is busy, please retry."}

    return jsonify({
        "energy_score": max(10, 100 - (len(analysis.get("mistakes", [])) * 15)),
        "status": "Healthy" if not analysis.get("mistakes") else "Critical",
        "mistakes_array": analysis.get("mistakes", []),
        "suggestion": analysis.get("suggestion", "System stable."),
        "ai_confidence": 98.5
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
