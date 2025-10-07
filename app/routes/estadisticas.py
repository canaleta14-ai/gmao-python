from flask import Blueprint, jsonify
from flask_login import login_required
from app.controllers.estadisticas_controller import obtener_estadisticas

estadisticas_bp = Blueprint("estadisticas", __name__, url_prefix="/api/estadisticas")


@estadisticas_bp.route("", methods=["GET"])
@login_required
def estadisticas():
    """Endpoint de estadísticas del dashboard.

    Debe ser robusto ante BD vacía o errores internos y devolver
    un JSON válido con valores por defecto para evitar errores 500.
    """
    try:
        data = obtener_estadisticas()
        # Asegurar estructura mínima
        if not isinstance(data, dict):
            data = {}
        data.setdefault("ordenes_por_estado", {})
        data.setdefault("ordenes_ultima_semana", 0)
        data.setdefault("activos_por_estado", {})
        data.setdefault("total_activos", 0)
        return jsonify(data), 200
    except Exception:
        # Ante cualquier error, devolver estructura vacía y 200 para que el frontend no falle
        return jsonify(
            {
                "ordenes_por_estado": {},
                "ordenes_ultima_semana": 0,
                "activos_por_estado": {},
                "total_activos": 0,
            }
        ), 200
