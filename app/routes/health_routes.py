from flask import Blueprint

health_bp = Blueprint("health", __name__)

@health_bp.route("/", methods=["GET"])
def health():
    return {
        "message": "Logistica Backend API UP",
    }, 200