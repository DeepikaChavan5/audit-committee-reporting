# middleware/sanitize.py

import re
from flask import request, jsonify, g

# Basic HTML tag removal
def strip_html(text):
    clean = re.compile(r'<.*?>')
    return re.sub(clean, '', text)

# Detect prompt injection patterns
def detect_prompt_injection(text):
    patterns = [
        r"ignore previous instructions",
        r"disregard rules",
        r"system prompt",
        r"act as",
        r"bypass",
        r"jailbreak"
    ]

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

# Middleware function
def sanitize_input():
    if request.method == "POST":
        data = request.get_json(silent=True)

        # ✅ Check valid JSON
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid input format"}), 400

        user_input = data.get("message", "")

        # ✅ Ensure input is string
        if not isinstance(user_input, str):
            return jsonify({"error": "Message must be a string"}), 400

        # ✅ Strip HTML tags
        cleaned_input = strip_html(user_input)

        # ✅ Detect prompt injection
        if detect_prompt_injection(cleaned_input):
            return jsonify({
                "error": "Prompt injection detected. Request blocked."
            }), 400

        # ✅ Store cleaned input safely (DO NOT modify request.json directly)
        g.cleaned_data = data
        g.cleaned_data["message"] = cleaned_input