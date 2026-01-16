import os, re, json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- Gemini Configuration ---
GEMINI_API_KEY = "AIzaSyBI3rUVdXleb1skfn6UZaK3VAihED9rg7c" 
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_gemini_analysis(code_content, filename):
    try:
        # Gemini ko instruction di ja rahi hai ke wo JSON format mein result de
        prompt = f"""
        Act as an expert Security Researcher and Senior Developer. 
        Analyze the following code from the file '{filename}'.
        
        Identify any:
        1. Security vulnerabilities (hardcoded keys, injection risks).
        2. Syntax or logical errors.
        3. Performance bottlenecks.

        Return ONLY a JSON object with this structure:
        {{
            "mistakes": ["List each specific error found"],
            "suggestion": "A 2-sentence optimization strategy",
            "score_deduction": 15 (integer value to deduct per mistake)
        }}

        Code Content:
        {code_content[:3000]}
        """
        
        response = model.generate_content(prompt)
        
        # Cleaning response text to ensure it's valid JSON
        json_text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(json_text)
    except Exception as e:
        print(f"Gemini Error: {e}")
        return {
            "mistakes": ["AI Uplink Busy: Could not perform deep neural scan."],
            "suggestion": "Ensure code integrity manually while AI nodes resync.",
            "score_deduction": 0
        }

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return "EcoSync AI Core (Gemini Fully Integrated) is Online."
    
    if 'file' not in request.files: 
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    try:
        content = file.read().decode('utf-8', errors='ignore')
        
        # 1. Gemini se poora Audit karwao
        analysis = get_gemini_analysis(content, file.filename)
        
        mistakes = analysis.get("mistakes", [])
        mistake_count = len(mistakes)
        
        # 2. Dynamic Score Calculation
        # Har galti par score kam hoga
        score = max(5, 100 - (mistake_count * analysis.get("score_deduction", 10)))

        return jsonify({
            "energy_score": score,
            "status": "Healthy" if mistake_count == 0 else "Critical",
            "mistakes_array": mistakes,
            "suggestion": analysis.get("suggestion", "System optimal."),
            "ai_confidence": 98 if mistake_count == 0 else 85,
            "chart_data": [score-8, score-4, score-12, score-3, score]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
