from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from app.controllers.planes_controller import (
    listar_planes,
    crear_plan,
    obtener_plan_por_id,
    editar_plan,
    eliminar_plan,
    obtener_estadisticas_planes,
    generar_ordenes_automaticas,
    generar_ordenes_manuales,
)

planes_bp = Blueprint("planes", __name__, url_prefix="/planes")


@planes_bp.route("/")
@login_required
def planes_page():
    """Página principal de planes de mantenimiento"""
    return render_template("preventivo/preventivo.html", section="preventivo")


@planes_bp.route("/api", methods=["GET", "POST"])
@login_required
def planes_api():
    if request.method == "GET":
        return jsonify(listar_planes())
    elif request.method == "POST":
        try:
            data = request.get_json()
            print(f"Datos recibidos: {data}")  # Debug
            nuevo_plan = crear_plan(data)
            return jsonify(
                {
                    "success": True,
                    "message": f"Plan creado exitosamente con código {nuevo_plan.codigo_plan}",
                    "plan": {
                        "id": nuevo_plan.id,
                        "codigo": nuevo_plan.codigo_plan,
                        "nombre": nuevo_plan.nombre,
                    },
                }
            )
        except ValueError as e:
            print(f"Error de validación: {e}")  # Debug
            return jsonify({"success": False, "error": str(e)}), 400
        except Exception as e:
            print(f"Error interno: {e}")  # Debug
            import traceback

            traceback.print_exc()
            return (
                jsonify(
                    {"success": False, "error": f"Error interno del servidor: {str(e)}"}
                ),
                500,
            )


@planes_bp.route("/api/<int:plan_id>", methods=["GET", "PUT", "DELETE"])
@login_required
def plan_individual(plan_id):
    if request.method == "GET":
        # Obtener detalles de un plan específico
        try:
            plan_data = obtener_plan_por_id(plan_id)
            return jsonify({"success": True, "plan": plan_data})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 404

    elif request.method == "PUT":
        # Editar un plan existente
        try:
            data = request.get_json()
            print(f"Editando plan {plan_id} con datos: {data}")  # Debug
            plan_editado = editar_plan(plan_id, data)
            return jsonify(
                {
                    "success": True,
                    "message": f"Plan {plan_editado.codigo_plan} editado exitosamente",
                    "plan": {
                        "id": plan_editado.id,
                        "codigo": plan_editado.codigo_plan,
                        "nombre": plan_editado.nombre,
                    },
                }
            )
        except ValueError as e:
            print(f"Error de validación en edición: {e}")  # Debug
            return jsonify({"success": False, "error": str(e)}), 400
        except Exception as e:
            print(f"Error interno en edición: {e}")  # Debug
            import traceback

            traceback.print_exc()
            return jsonify({"success": False, "error": f"Error interno: {str(e)}"}), 500

    elif request.method == "DELETE":
        # Eliminar un plan
        try:
            eliminar_plan(plan_id)
            return jsonify({"success": True, "message": "Plan eliminado exitosamente"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


@planes_bp.route("/api/estadisticas")
@login_required
def estadisticas_planes():
    """Obtener estadísticas de planes de mantenimiento"""
    try:
        stats = obtener_estadisticas_planes()
        return jsonify(stats)
    except Exception as e:
        return (
            jsonify({"success": False, "error": "Error al obtener estadísticas"}),
            500,
        )


@planes_bp.route("/api/generar-ordenes", methods=["POST"])
@login_required
def generar_ordenes_preventivo():
    """Generar órdenes automáticamente desde planes vencidos"""
    try:
        resultado = generar_ordenes_automaticas()
        return jsonify(resultado)
    except Exception as e:
        print(f"Error en endpoint generar-ordenes: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@planes_bp.route("/api/generar-ordenes-manual", methods=["POST"])
@login_required
def generar_ordenes_manual():
    """Generar órdenes manualmente para planes sin generación automática"""
    try:
        # Obtener usuario si está disponible (opcional)
        usuario = "Usuario Manual"  # Se puede mejorar para obtener el usuario actual

        resultado = generar_ordenes_manuales(usuario)
        return jsonify(resultado)
    except Exception as e:
        print(f"Error en endpoint generar-ordenes-manual: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
