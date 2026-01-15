import os, re, json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def scan_file_for_mistakes(content):
    mistakes = []
    # 1. Merge Conflicts Check
    if "<<<<<<< HEAD" in content or "=======" in content:
        mistakes.append("CRITICAL: Git Merge Conflict markers detected.")
    
    # 2. Security Check (Hardcoded Password)
    if "ashna@123" in content or re.search(r'pass:\s*["\'].+["\']', content):
        mistakes.append("SECURITY: Hardcoded credentials found (ashna@123).")
    
    # 3. Firebase Path Check
    if 'JSON.parse("./' in content:
        mistakes.append("LOGIC: Invalid Firebase JSON parsing method.")
        
    # 4. Protocol Redundancy
    if "axios" in content and "nodemailer" in content:
        mistakes.append("SYNC: Redundant email protocols (Axios + Nodemailer).")

    return mistakes

@app.route('/analyze', methods=['POST'])
def analyze_data():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    
    file = request.files['file']
    try:
        content = file.read().decode('utf-8', errors='ignore')
        mistakes = scan_file_for_mistakes(content)
        
        # REAL LOGIC: Score calculation
        mistake_count = len(mistakes)
        # Agar koi ghalti nahi to 100%, warna har ghalti par 25% kam
        score = max(10, 100 - (mistake_count * 25))
        
        status = "Stable" if mistake_count == 0 else "Critical"
        
        # Radar Data: [Security, Performance, Stability, Logic, Sync]
        # Har category ko mistake ke hisab se real values dena
        radar = [
            20 if "SECURITY" in str(mistakes) else 95, # Security
            score,                                     # Performance
            40 if "CRITICAL" in str(mistakes) else 90, # Stability
            30 if "LOGIC" in str(mistakes) else 95,    # Logic
            30 if "SYNC" in str(mistakes) else 90      # Sync
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
    app.run(debug=True, port=5005)