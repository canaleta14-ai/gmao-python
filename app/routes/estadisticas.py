from flask import Blueprint, jsonify
from flask_login import login_required
from app.controllers.estadisticas_controller import obtener_estadisticas

estadisticas_bp = Blueprint("estadisticas", __name__, url_prefix="/api/estadisticas")


@estadisticas_bp.route("", methods=["GET"])
@login_required
def estadisticas():
    return jsonify(obtener_estadisticas())
