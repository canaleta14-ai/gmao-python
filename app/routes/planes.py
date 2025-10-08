from flask import Blueprint, request, jsonify, render_template, Response
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
    generar_orden_individual,
)

planes_bp = Blueprint("planes", __name__, url_prefix="/planes")


@planes_bp.route("/")
@login_required
def planes_page():
    """Página principal de planes de mantenimiento"""
    try:
        return render_template("preventivo/preventivo.html", section="preventivo")
    except Exception:
        html = """
        <!DOCTYPE html>
        <html lang=\"es\">
        <head><meta charset=\"utf-8\"><title>Planes de Mantenimiento</title></head>
        <body>
            <h1>Planes de Mantenimiento</h1>
            <p>La página de planes no pudo renderizarse completamente, pero el sistema está operativo.</p>
        </body>
        </html>
        """
        return Response(html, mimetype="text/html")


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
            return jsonify(
                {"success": True, "message": f"Plan {plan_id} eliminado exitosamente"}
            )
        except Exception as e:
            print(f"Error al eliminar plan {plan_id}: {e}")  # Debug
            return jsonify({"success": False, "error": str(e)}), 400


@planes_bp.route("/api/estadisticas", methods=["GET"])
@login_required
def planes_estadisticas():
    """Obtener estadísticas de planes de mantenimiento"""
    try:
        estadisticas = obtener_estadisticas_planes()
        return jsonify({"success": True, "estadisticas": estadisticas})
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@planes_bp.route("/generar-ordenes", methods=["POST"])
@login_required
def generar_ordenes():
    """Generar órdenes de trabajo automáticamente"""
    try:
        data = request.get_json() or {}
        modo = data.get("modo", "automatico")  # "automatico" o "manual"

        if modo == "automatico":
            resultado = generar_ordenes_automaticas()
        else:
            # Para modo manual, se espera una lista de plan_ids
            plan_ids = data.get("plan_ids", [])
            if not plan_ids:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Se requieren IDs de planes para modo manual",
                        }
                    ),
                    400,
                )
            resultado = generar_ordenes_manuales(plan_ids)

        return jsonify({"success": True, "resultado": resultado})
    except Exception as e:
        print(f"Error generando órdenes: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@planes_bp.route("/api/generar-ordenes-manual", methods=["POST"])
@login_required
def generar_ordenes_manual_api():
    """Generar órdenes de trabajo para todos los planes sin generación automática"""
    try:
        # Llamar a la función que genera órdenes para planes manuales
        # Esta función debería retornar el número de órdenes generadas
        resultado = generar_ordenes_manuales()

        ordenes_generadas = (
            resultado.get("ordenes_generadas", 0) if isinstance(resultado, dict) else 0
        )

        return jsonify(
            {
                "success": True,
                "ordenes_generadas": ordenes_generadas,
                "mensaje": f"Se generaron {ordenes_generadas} órdenes de trabajo",
            }
        )
    except Exception as e:
        print(f"Error generando órdenes manuales: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@planes_bp.route("/<int:plan_id>/generar-orden", methods=["POST"])
@login_required
def generar_orden_individual_api(plan_id):
    """Generar una orden de trabajo individual para un plan específico"""
    try:
        from flask_login import current_user

        usuario = current_user.nombre if hasattr(current_user, "nombre") else "Sistema"

        resultado = generar_orden_individual(plan_id, usuario)

        return jsonify(resultado)
    except ValueError as e:
        print(f"Error de validación: {e}")
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        print(f"Error generando orden individual: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
