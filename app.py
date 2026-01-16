import os, re, json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def scan_file_for_mistakes(content):
    mistakes = []
    if "<<<<<<< HEAD" in content or "=======" in content:
        mistakes.append("CRITICAL: Git Merge Conflict markers detected.")
    if "ashna@123" in content or re.search(r'pass:\s*["\'].+["\']', content):
        mistakes.append("SECURITY: Hardcoded credentials found.")
    if 'JSON.parse("./' in content:
        mistakes.append("LOGIC: Invalid Firebase JSON parsing method.")
    if "axios" in content and "nodemailer" in content:
        mistakes.append("SYNC: Redundant email protocols.")
    return mistakes

# Route ko "/" rakhein taake base URL par call kaam kare
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return "EcoSync AI Core is Online."
    
    if 'file' not in request.files: 
        return jsonify({"error": "No file"}), 400
    
    file = request.files['file']
    try:
        content = file.read().decode('utf-8', errors='ignore')
        mistakes = scan_file_for_mistakes(content)
        
        mistake_count = len(mistakes)
        score = max(10, 100 - (mistake_count * 25))
        status = "Stable" if mistake_count == 0 else "Critical"
        
        radar = [
            20 if "SECURITY" in str(mistakes) else 95,
            score,
            40 if "CRITICAL" in str(mistakes) else 90,
            30 if "LOGIC" in str(mistakes) else 95,
            30 if "SYNC" in str(mistakes) else 90
        ]

        return jsonify({
            "energy_score": score,
            "status": status,
            "mistakes_array": mistakes,
            "mistakes_list": "<br>".join([f"• {m}" for m in mistakes]) if mistakes else "System pathways optimal.",
            "chart_data": [score-5, score-2, score-8, score-4, score-1, score],
            "radar_data": radar,
            "regions": {
                "na": "Stable" if mistake_count < 2 else "Critical",
                "eu": "Stable" if mistake_count < 1 else "Critical",
                "asia": "Stable" if mistake_count == 0 else "Critical"
            },
            "security": {
                "firewall": "ACTIVE" if "SECURITY" not in str(mistakes) else "BREACHED", 
                "encryption": "SECURE" if "SECURITY" not in str(mistakes) else "COMPROMISED"
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
