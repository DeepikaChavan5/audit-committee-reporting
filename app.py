from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from middleware.sanitize import sanitize_input

app = Flask(__name__)

app.before_request(sanitize_input)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["30 per minute"]
)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Rate limit exceeded",
        "retry_after": e.retry_after if hasattr(e, "retry_after") else "Try again later"
    }), 429


# ✅ ADD THIS HERE (IMPORTANT)
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


@app.route("/")
def home():
    return "API is running"

@app.route("/health")
def health():
    return "OK"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    return jsonify({"response": data.get("message")})

@app.route("/generate-report", methods=["POST"])
@limiter.limit("10 per minute")
def generate_report():
    return jsonify({"message": "Report generated successfully"})


if __name__ == "__main__":
    app.run(debug=False)