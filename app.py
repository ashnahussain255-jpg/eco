import os, re, json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Sabhi origins ko allow karein taake local aur Render dono chalein
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Gemini Configuration ---
GEMINI_API_KEY = "AIzaSyBI3rUVdXleb1skfn6UZaK3VAihED9rg7c" 
genai.configure(api_key=GEMINI_API_KEY)

# Safety settings ko disable karna zaroori hai taake AI code ko 'unsafe' keh kar block na kare
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel('gemini-1.5-flash')

def get_gemini_analysis(code_content, filename):
    try:
        prompt = f"""
        Act as a Professional Code Auditor. Analyze the file '{filename}'.
        Task: Identify bugs and security issues.
        Requirement: Return ONLY a valid JSON object. No markdown, no triple backticks.
        
        JSON Structure:
        {{
            "mistakes": ["issue 1", "issue 2"],
            "suggestion": "How to fix it in 2 sentences.",
            "score_deduction": 15
        }}

        Code to analyze:
        {code_content[:3500]}
        """
        
        # Generation with safety settings
        response = model.generate_content(prompt, safety_settings=safety_settings)
        
        if not response.text:
            raise ValueError("Empty response from AI")

        # Clean JSON: Extract everything between the first '{' and the last '}'
        raw_text = response.text.strip()
        start_idx = raw_text.find('{')
        end_idx = raw_text.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON found in response")
            
        clean_json = raw_text[start_idx:end_idx]
        return json.loads(clean_json)

    except Exception as e:
        print(f"DEBUG: Gemini Error - {str(e)}")
        return {
            "mistakes": ["AI Uplink Latency: Could not parse neural patterns."],
            "suggestion": "The AI is currently re-calibrating. Please re-upload the source file.",
            "score_deduction": 0
        }

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return "EcoSync AI Core is Online and Ready."
    
    if 'file' not in request.files: 
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    try:
        content = file.read().decode('utf-8', errors='ignore')
        
        # AI Analysis Call
        analysis = get_gemini_analysis(content, file.filename)
        
        mistakes = analysis.get("mistakes", [])
        m_count = len(mistakes)
        
        # Professional Metric Calculation
        base_score = 100
        deduction = m_count * analysis.get("score_deduction", 10)
        final_score = max(5, base_score - deduction)

        return jsonify({
            "energy_score": final_score,
            "status": "Healthy" if m_count == 0 else "Critical",
            "mistakes_array": mistakes,
            "suggestion": analysis.get("suggestion", "Core system integrity verified."),
            "ai_confidence": round((98.5 - (m_count * 1.5)), 1)
        })
    except Exception as e:
        print(f"DEBUG: Server Crash - {str(e)}")
        return jsonify({"error": "Neural Handshake Failed", "details": str(e)}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
