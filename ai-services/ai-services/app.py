from flask import Flask, request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from flask_talisman import Talisman
from middleware.sanitize import sanitize_input

app = Flask(__name__)

# -------------------------------
# 🔐 JWT CONFIG
# -------------------------------
app.config["JWT_SECRET_KEY"] = "super-secret-key"

jwt = JWTManager(app)

# -------------------------------
# 🔐 SECURITY HEADERS
# -------------------------------
Talisman(app, content_security_policy={
    'default-src': "'self'"
})

# -------------------------------
# 🛡️ INPUT SANITIZATION
# -------------------------------
app.before_request(sanitize_input)

# -------------------------------
# 🚦 RATE LIMITING
# -------------------------------
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["5 per minute"]
)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Rate limit exceeded"
    }), 429


# -------------------------------
# 🔒 EXTRA SECURITY HEADERS
# -------------------------------
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


# -------------------------------
# 🔐 JWT ERROR HANDLING
# -------------------------------
@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "msg": "Missing token"
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        "msg": "Invalid token"
    }), 401


# -------------------------------
# ✅ BASIC ROUTES
# -------------------------------
@app.route("/")
def home():
    return "API is running"


@app.route("/health")
def health():
    return "OK"


@app.route("/check")
def check():
    return "WORKING"


# -------------------------------
# ✅ LOGIN API
# -------------------------------
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "No data received"
        }), 400

    username = data.get("username")
    password = data.get("password")

    if username == "admin" and password == "1234":

        token = create_access_token(identity="admin")

        return jsonify({
            "token": token
        }), 200

    return jsonify({
        "error": "Invalid credentials"
    }), 401


# -------------------------------
# 🔐 PROTECTED CHAT API
# -------------------------------
@app.route("/chat", methods=["POST"])
@jwt_required()
def chat():

    data = getattr(g, "cleaned_data", request.get_json())

    message = data.get("message", "")

    return jsonify({
        "response": f"You said: {message}"
    })


# -------------------------------
# 🔐 ROLE-BASED REPORT API
# -------------------------------
@app.route("/generate-report", methods=["POST"])
@jwt_required()
@limiter.limit("3 per minute")
def generate_report():

    user = get_jwt_identity()

    # ✅ ROLE CHECK
    if user != "admin":
        return jsonify({
            "msg": "Forbidden"
        }), 403

    return jsonify({
        "message": "Report generated successfully"
    })


# -------------------------------
# 🚀 RUN SERVER
# -------------------------------
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )