"""
Rutas para el módulo de personal
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from functools import wraps

# Blueprint para personal
personal_bp = Blueprint("personal", __name__, url_prefix="/personal")


def login_required_json(f):
    """Decorador para rutas que requieren login y devuelven JSON"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user

        if not current_user.is_authenticated:
            return jsonify({"error": "No autorizado"}), 401
        return f(*args, **kwargs)

    return decorated_function


@personal_bp.route("/")
@login_required
def personal_page():
    """Página principal de personal"""
    return render_template("personal/personal.html", section="personal")
