from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    make_response,
    send_file,
    current_app,
)
from flask_login import login_required, current_user
from app.controllers.ordenes_controller import (
    listar_ordenes,
    listar_ordenes_paginado,
    obtener_orden,
    crear_orden,
    actualizar_orden,
    actualizar_estado_orden as actualizar_estado_orden_controller,
    eliminar_orden,
    obtener_activos_disponibles,
    obtener_tecnicos_disponibles,
    obtener_estadisticas_ordenes,
    exportar_ordenes_csv,
)
from app.controllers.archivos_controller import (
    subir_archivo,
    listar_archivos_orden,
    eliminar_archivo,
    descargar_archivo,
    agregar_enlace,
)
import os

ordenes_bp = Blueprint("ordenes", __name__, url_prefix="/ordenes")


@ordenes_bp.route("/")
@login_required
def ordenes_page():
    """Página principal de órdenes de trabajo"""
    return render_template("ordenes/ordenes.html", section="ordenes")


@ordenes_bp.route("/api", methods=["GET"])
@login_required
def listar_ordenes_api():
    """API para listar órdenes de trabajo"""
    try:
        estado = request.args.get("estado")
        limit = request.args.get("limit")

        # Si se solicita paginación, usar la función paginada
        page = request.args.get("page", type=int)
        per_page = request.args.get("per_page", type=int)
        q = request.args.get("q")
        tipo = request.args.get("tipo")
        prioridad = request.args.get("prioridad")

        if page is not None:
            # Usar paginación
            per_page = per_page or 10
            resultado = listar_ordenes_paginado(
                page, per_page, q, estado, tipo, prioridad
            )
            return jsonify(resultado)
        else:
            # Usar listado tradicional sin paginación
            ordenes = listar_ordenes(estado, limit)
            return jsonify(ordenes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ordenes_bp.route("/", methods=["POST"])
@login_required
def crear_orden_api():
    """API para crear nueva orden de trabajo"""
    try:
        data = request.get_json()

        # Validar datos requeridos
        if not data.get("tipo"):
            return jsonify({"error": "El tipo es requerido"}), 400
        if not data.get("prioridad"):
            return jsonify({"error": "La prioridad es requerida"}), 400
        if not data.get("descripcion"):
            return jsonify({"error": "La descripción es requerida"}), 400

        nueva_orden = crear_orden(data)
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Orden de trabajo creada exitosamente",
                    "numero_orden": nueva_orden.numero_orden,
                    "id": nueva_orden.id,
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500


@ordenes_bp.route("/api/<int:id>", methods=["GET"])
@login_required
def obtener_orden_api(id):
    """API para obtener una orden específica"""
    try:
        orden = obtener_orden(id)
        return jsonify(orden)
    except Exception as e:
        return jsonify({"error": "Orden no encontrada"}), 404


@ordenes_bp.route("/api/<int:id>", methods=["PUT"])
@login_required
def actualizar_orden_api(id):
    """API para actualizar orden de trabajo"""
    try:
        data = request.get_json()
        orden = actualizar_orden(id, data)
        return jsonify({"success": True, "message": "Orden actualizada exitosamente"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500


@ordenes_bp.route("/api/<int:id>/estado", methods=["PUT"])
@login_required
def actualizar_estado_orden(id):
    """API para actualizar estado de una orden"""
    try:
        data = request.get_json()

        if not data.get("estado"):
            return jsonify({"error": "El estado es requerido"}), 400

        orden = actualizar_estado_orden_controller(id, data)
        return jsonify({"success": True, "message": "Estado actualizado exitosamente"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500


@ordenes_bp.route("/api/<int:id>", methods=["DELETE"])
@login_required
def eliminar_orden_api(id):
    """API para eliminar orden de trabajo"""
    try:
        eliminar_orden(id)
        return jsonify({"success": True, "message": "Orden eliminada exitosamente"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500


@ordenes_bp.route("/activos", methods=["GET"])
@login_required
def obtener_activos():
    """API para obtener activos disponibles"""
    try:
        activos = obtener_activos_disponibles()
        return jsonify(activos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ordenes_bp.route("/tecnicos", methods=["GET"])
@login_required
def obtener_tecnicos():
    """API para obtener técnicos disponibles"""
    try:
        tecnicos = obtener_tecnicos_disponibles()
        return jsonify(tecnicos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ordenes_bp.route("/estadisticas", methods=["GET"])
@login_required
def obtener_estadisticas():
    """API para obtener estadísticas de órdenes"""
    try:
        stats = obtener_estadisticas_ordenes()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ordenes_bp.route("/exportar-csv", methods=["GET"])
@login_required
def exportar_csv():
    """Exportar órdenes de trabajo a Excel"""
    try:
        excel_data = exportar_ordenes_csv()

        response = make_response(excel_data)
        response.headers["Content-Type"] = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response.headers["Content-Disposition"] = (
            "attachment; filename=ordenes_trabajo.xlsx"
        )

        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Rutas para gestión de archivos adjuntos


@ordenes_bp.route("/api/<int:orden_id>/archivos", methods=["POST"])
@login_required
def subir_archivo_orden(orden_id):
    """Subir archivo adjunto a una orden de trabajo"""
    try:
        resultado = subir_archivo(orden_id, current_user.id)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ordenes_bp.route("/api/<int:orden_id>/archivos", methods=["GET"])
@login_required
def obtener_archivos_orden(orden_id):
    """Obtener lista de archivos adjuntos de una orden"""
    try:
        archivos = listar_archivos_orden(orden_id)
        return jsonify(archivos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ordenes_bp.route("/api/<int:orden_id>/enlaces", methods=["POST"])
@login_required
def agregar_enlace_orden(orden_id):
    """Agregar enlace externo a una orden de trabajo"""
    try:
        data = request.get_json()
        if not data.get("url"):
            return jsonify({"error": "La URL es requerida"}), 400

        resultado = agregar_enlace(orden_id, data, current_user.id)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ordenes_bp.route("/api/archivos/<int:archivo_id>", methods=["DELETE"])
@login_required
def eliminar_archivo_adjunto(archivo_id):
    """Eliminar archivo adjunto"""
    try:
        eliminar_archivo(archivo_id)
        return jsonify({"mensaje": "Archivo eliminado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ordenes_bp.route("/api/archivos/<int:archivo_id>/download", methods=["GET"])
@login_required
def descargar_archivo_adjunto(archivo_id):
    """Descargar archivo adjunto"""
    try:
        archivo_path, nombre_original = descargar_archivo(archivo_id)
        return send_file(
            archivo_path, as_attachment=True, download_name=nombre_original
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
