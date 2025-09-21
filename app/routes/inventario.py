from flask import Blueprint, request, jsonify, render_template
from app.controllers.inventario_controller import (
    listar_inventario,
    crear_item,
    registrar_movimiento,
)

inventario_bp = Blueprint("inventario", __name__, url_prefix="/inventario")


@inventario_bp.route("/")
def inventario_page():
    """Página principal de inventario"""
    return render_template("inventario/inventario.html", section="inventario")


@inventario_bp.route("/api", methods=["GET", "POST"])
def inventario_api():
    if request.method == "GET":
        return jsonify(listar_inventario())
    elif request.method == "POST":
        data = request.get_json()
        crear_item(data)
        return jsonify({"success": True, "message": "Item creado exitosamente"})


@inventario_bp.route("/api/<int:id>/movimiento", methods=["POST"])
def movimiento_inventario(id):
    data = request.get_json()
    registrar_movimiento(id, data)
    return jsonify({"success": True, "message": "Movimiento registrado exitosamente"})
