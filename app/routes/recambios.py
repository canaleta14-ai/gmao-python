from flask import Blueprint, request, jsonify
from app.controllers import orden_recambios_controller
from app.models import OrdenTrabajo

recambios_bp = Blueprint("recambios", __name__)


@recambios_bp.route("/ordenes/<int:orden_id>/recambios", methods=["GET"])
def obtener_recambios(orden_id):
    """Obtener todos los recambios de una orden"""
    try:
        recambios = orden_recambios_controller.obtener_recambios_orden(orden_id)
        return jsonify({"success": True, "recambios": recambios})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@recambios_bp.route("/ordenes/<int:orden_id>/recambios", methods=["POST"])
def agregar_recambio(orden_id):
    """Agregar un recambio a una orden"""
    try:
        data = request.get_json()

        required_fields = ["inventario_id", "cantidad_solicitada"]
        for field in required_fields:
            if field not in data:
                return (
                    jsonify({"success": False, "error": f"Campo requerido: {field}"}),
                    400,
                )

        recambio = orden_recambios_controller.agregar_recambio_a_orden(
            orden_id=orden_id,
            inventario_id=data["inventario_id"],
            cantidad_solicitada=data["cantidad_solicitada"],
            observaciones=data.get("observaciones"),
        )

        return jsonify(
            {
                "success": True,
                "message": "Recambio agregado exitosamente",
                "recambio": (
                    recambio.to_dict()
                    if hasattr(recambio, "to_dict")
                    else str(recambio)
                ),
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@recambios_bp.route("/recambios/<int:recambio_id>", methods=["PUT"])
def actualizar_recambio(recambio_id):
    """Actualizar la cantidad utilizada de un recambio"""
    try:
        data = request.get_json()

        if "cantidad_utilizada" not in data:
            return (
                jsonify(
                    {"success": False, "error": "Campo requerido: cantidad_utilizada"}
                ),
                400,
            )

        recambio = orden_recambios_controller.actualizar_cantidad_utilizada(
            recambio_id=recambio_id, cantidad_utilizada=data["cantidad_utilizada"]
        )

        return jsonify(
            {
                "success": True,
                "message": "Cantidad actualizada exitosamente",
                "recambio": recambio,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@recambios_bp.route("/recambios/<int:recambio_id>", methods=["DELETE"])
def eliminar_recambio(recambio_id):
    """Eliminar un recambio de una orden"""
    try:
        resultado = orden_recambios_controller.eliminar_recambio(recambio_id)

        return jsonify({"success": True, "message": resultado["mensaje"]})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@recambios_bp.route("/ordenes/<int:orden_id>/recambios/descontar", methods=["POST"])
def descontar_recambios(orden_id):
    """Descontar del stock todos los recambios de una orden"""
    try:
        data = request.get_json() or {}
        usuario_id = data.get("usuario_id", "sistema")
        es_automatico = data.get("es_automatico", False)

        resultado = orden_recambios_controller.descontar_recambios_orden(
            orden_id=orden_id, usuario_id=usuario_id, es_automatico=es_automatico
        )

        return jsonify(
            {
                "success": True,
                "message": resultado["mensaje"],
                "recambios_descontados": resultado["recambios_descontados"],
                "errores": resultado["errores"],
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
