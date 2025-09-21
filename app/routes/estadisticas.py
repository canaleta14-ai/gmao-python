from flask import Blueprint, jsonify
from app.controllers.estadisticas_controller import obtener_estadisticas

estadisticas_bp = Blueprint("estadisticas", __name__, url_prefix="/api/estadisticas")


@estadisticas_bp.route("", methods=["GET"])
def estadisticas():
    return jsonify(obtener_estadisticas())
