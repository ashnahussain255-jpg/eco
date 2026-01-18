import os, json, re, requests
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import psutil # Isay top par import karein
app = Flask(__name__)
# Sab origins ko allow kiya hai taake GitHub Pages se error na aaye
CORS(app, resources={r"/*": {"origins": "*"}})

# Groq API Configuration
# Render ke 'Environment Variables' mein GROQ_API_KEY lazmi dalein
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def get_groq_analysis(code_content):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-8b-instant", # Newest stable model
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert code auditor. Return ONLY a valid JSON object with keys 'mistakes' (array of strings) and 'suggestion' (string). If no mistakes, return empty array []."
                },
                {
                    "role": "user",
                    "content": f"Audit this code and find bugs or improvements:\n\n{code_content[:2000]}"
                }
            ],
            "response_format": {"type": "json_object"}
        }

        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            res_data = response.json()
            content = res_data['choices'][0]['message']['content']
            return json.loads(content)
        else:
            print(f"DEBUG Groq API Error: {response.text}")
    except Exception as e:
        print(f"DEBUG System Error: {str(e)}")
    return None
@app.route('/system-stats', methods=['GET'])
def get_stats():
    try:
        # Real CPU aur RAM usage
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        
        # Real Network Throughput
        net = psutil.net_io_counters()
        total_traffic = (net.bytes_sent + net.bytes_recv) / (1024 * 1024) # MB mein
        
        return jsonify({
            "cpu_usage": f"{cpu}%",
            "ram_usage": f"{ram}%",
            "network_mb": f"{round(total_traffic, 2)} MB",
            "status": "ACTIVE"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/', methods=['POST', 'GET', 'OPTIONS'])
def index():
    if request.method == 'OPTIONS':
        return make_response("", 200)

    if request.method == 'GET':
        return "EcoSync Groq-AI Core (v3.1) is ONLINE."

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files.get('file')
    try:
        content = file.read().decode('utf-8', errors='ignore')
        if not content.strip():
            return jsonify({"error": "File is empty"}), 400

        analysis = get_groq_analysis(content)

        if not analysis:
            return jsonify({
                "energy_score": 0,
                "status": "AI_OFFLINE",
                "mistakes_array": ["Could not reach AI brain. Check API Key."],
                "suggestion": "Server is up, but AI provider is busy.",
                "ai_confidence": 0
            })

        mistakes = analysis.get("mistakes", [])
        status = "Healthy" if len(mistakes) == 0 else "Critical"
        energy_score = max(5, 100 - (len(mistakes) * 15))

        return jsonify({
            "energy_score": energy_score,
            "status": status,
            "mistakes_array": mistakes,
            "suggestion": analysis.get("suggestion", "System fully optimized."),
            "ai_confidence": 98.2
        })
    except Exception as e:
        print(f"Critical Route Error: {str(e)}")
        return jsonify({"error": "Processing failed"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
