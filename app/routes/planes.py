from flask import Blueprint, request, jsonify, render_template
from app.controllers.planes_controller import listar_planes, crear_plan

planes_bp = Blueprint("planes", __name__, url_prefix="/planes")


@planes_bp.route("/")
def planes_page():
    """Página principal de planes de mantenimiento"""
    return render_template("preventivo/preventivo.html", section="preventivo")


@planes_bp.route("/api", methods=["GET", "POST"])
def planes_api():
    if request.method == "GET":
        return jsonify(listar_planes())
    elif request.method == "POST":
        data = request.get_json()
        crear_plan(data)
        return jsonify({"success": True, "message": "Plan creado exitosamente"})
