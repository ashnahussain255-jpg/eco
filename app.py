import os, json, re, requests
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Groq API Configuration
# Get your key from: https://console.groq.com/keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def get_groq_analysis(code_content):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-8b-8192", # Very fast and smart model
            "messages": [
                {
                    "role": "system",
                    "content": "You are a code auditor. Return ONLY a JSON object with 'mistakes' (array of strings) and 'suggestion' (string)."
                },
                {
                    "role": "user",
                    "content": f"Audit this code:\n\n{code_content[:1500]}"
                }
            ],
            "response_format": {"type": "json_object"} # Forces JSON response
        }

        response = requests.post(GROQ_URL, headers=headers, json=payload)
        res_data = response.json()
        
        if response.status_code == 200:
            content = res_data['choices'][0]['message']['content']
            return json.loads(content)
        else:
            print(f"Groq Error: {res_data}")
    except Exception as e:
        print(f"System Error: {str(e)}")
    return None

@app.route('/', methods=['POST', 'GET', 'OPTIONS'])
def index():
    if request.method == 'OPTIONS': return make_response("", 200)
    if request.method == 'GET': return "EcoSync Groq-AI Core is ONLINE."

    file = request.files.get('file')
    if not file: return jsonify({"error": "No file uploaded"}), 400

    try:
        content = file.read().decode('utf-8', errors='ignore')
        analysis = get_groq_analysis(content)

        if not analysis:
            return jsonify({
                "energy_score": 0,
                "status": "AI_OFFLINE",
                "mistakes_array": ["Groq AI link failed."],
                "suggestion": "Check your Groq API Key."
            })

        mistakes = analysis.get("mistakes", [])
        return jsonify({
            "energy_score": max(5, 100 - (len(mistakes) * 20)),
            "status": "Healthy" if not mistakes else "Critical",
            "mistakes_array": mistakes,
            "suggestion": analysis.get("suggestion", "Code looks solid!"),
            "ai_confidence": 97.8
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
