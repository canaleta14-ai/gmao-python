from flask import Blueprint, request, jsonify, render_template, Response
from app.controllers.activos_controller import (
    listar_activos,
    listar_activos_paginado,
    crear_activo,
    actualizar_activo,
    eliminar_activo,
    generar_siguiente_codigo,
    obtener_departamentos,
    exportar_activos_csv,
    validar_codigo_unico,
    obtener_estadisticas_activos,
    toggle_activo,
)

activos_bp = Blueprint("activos", __name__, url_prefix="/activos")


@activos_bp.route("/", methods=["GET", "POST"])
def activos_page():
    if request.method == "GET":
        """Página principal de activos"""
        return render_template("activos/activos.html", section="activos")
    elif request.method == "POST":
        data = request.get_json()
        nuevo_activo = crear_activo(data)
        return jsonify(
            {
                "success": True,
                "message": "Activo creado exitosamente",
                "id": nuevo_activo.id,
            }
        )


@activos_bp.route("/api", methods=["GET"])
def activos_list_api():
    """API para listar activos con soporte para filtros de búsqueda y paginación"""
    try:
        # Parámetros de paginación
        page = request.args.get("page", type=int)
        per_page = request.args.get("per_page", type=int)
        q = request.args.get("q")
        departamento = request.args.get("departamento")
        estado = request.args.get("estado")

        if page is not None:
            # Usar paginación
            per_page = per_page or 10
            resultado = listar_activos_paginado(page, per_page, q, departamento, estado)
            return jsonify(resultado)
        else:
            # Usar listado tradicional sin paginación
            filtros = {}
            # Recoger parámetros de filtro de la URL
            for param in [
                "nombre",
                "codigo",
                "ubicacion",
                "fabricante",
                "departamento",
                "tipo",
                "q",
                "limit",
            ]:
                if param in request.args:
                    filtros[param] = request.args[param]

            return jsonify(listar_activos(filtros if filtros else None))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@activos_bp.route("/api/<int:id>", methods=["GET", "PUT", "DELETE"])
def activo_detail(id):
    if request.method == "GET":
        # Para detalle, puedes crear una función en el controlador si lo deseas
        from app.models.activo import Activo

        activo = Activo.query.get_or_404(id)
        return jsonify(
            {
                "id": activo.id,
                "codigo": activo.codigo,
                "nombre": activo.nombre,
                "tipo": activo.tipo,
                "ubicacion": activo.ubicacion,
                "estado": activo.estado,
                "departamento": activo.departamento,
                "descripcion": activo.descripcion,
                "modelo": activo.modelo,
                "numero_serie": activo.numero_serie,
                "fabricante": activo.fabricante,
            }
        )
    elif request.method == "PUT":
        data = request.get_json()
        actualizar_activo(id, data)
        return jsonify({"success": True, "message": "Activo actualizado exitosamente"})
    elif request.method == "DELETE":
        eliminar_activo(id)
        return jsonify({"success": True, "message": "Activo eliminado exitosamente"})


@activos_bp.route("/departamentos", methods=["GET"])
def get_departamentos():
    """Obtiene la lista de departamentos"""
    return jsonify(obtener_departamentos())


@activos_bp.route("/generar-codigo/<departamento>", methods=["GET"])
def get_siguiente_codigo(departamento):
    """Genera el siguiente código para un departamento"""
    try:
        codigo = generar_siguiente_codigo(departamento)
        return jsonify({"codigo": codigo})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@activos_bp.route("/validar-codigo", methods=["POST"])
def validar_codigo():
    """Valida que un código sea único y tenga formato correcto"""
    try:
        data = request.get_json()
        if not data or "codigo" not in data:
            return jsonify({"error": "Código es requerido"}), 400

        resultado = validar_codigo_unico(data["codigo"])
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@activos_bp.route("/exportar-csv", methods=["GET"])
def exportar_csv():
    """Exporta todos los activos a CSV"""
    try:
        csv_data = exportar_activos_csv()

        response = Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=activos.csv"},
        )
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========== RUTAS PARA MANUALES ==========


@activos_bp.route("/api/<int:activo_id>/manuales", methods=["GET"])
def obtener_manuales(activo_id):
    """Obtener lista de manuales de un activo"""
    try:
        from app.controllers.manuales_controller import obtener_manuales_activo

        manuales = obtener_manuales_activo(activo_id)
        return jsonify(manuales), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@activos_bp.route("/api/<int:activo_id>/manuales", methods=["POST"])
def subir_manual(activo_id):
    """Subir un manual para un activo"""
    try:
        from app.controllers.manuales_controller import crear_manual

        # Verificar que se envió un archivo
        if "archivo" not in request.files:
            return jsonify({"mensaje": "No se envió ningún archivo"}), 400

        archivo = request.files["archivo"]
        if archivo.filename == "":
            return jsonify({"mensaje": "No se seleccionó ningún archivo"}), 400

        # Obtener datos adicionales
        tipo = request.form.get("tipo", "")
        descripcion = request.form.get("descripcion", "")

        # Crear manual
        manual = crear_manual(activo_id, archivo, tipo, descripcion)
        return jsonify(manual), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@activos_bp.route("/api/manuales/<int:manual_id>/descargar", methods=["GET"])
def descargar_manual(manual_id):
    """Descargar un manual"""
    try:
        from app.controllers.manuales_controller import descargar_manual_archivo

        return descargar_manual_archivo(manual_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@activos_bp.route("/api/manuales/<int:manual_id>/previsualizar", methods=["GET"])
def previsualizar_manual(manual_id):
    """Previsualizar un manual"""
    try:
        from app.controllers.manuales_controller import previsualizar_manual_archivo

        return previsualizar_manual_archivo(manual_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@activos_bp.route("/api/manuales/<int:manual_id>", methods=["DELETE"])
def eliminar_manual(manual_id):
    """Eliminar un manual"""
    try:
        from app.controllers.manuales_controller import eliminar_manual_archivo

        resultado = eliminar_manual_archivo(manual_id)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@activos_bp.route("/api/estadisticas", methods=["GET"])
def estadisticas_activos():
    """Obtener estadísticas de activos"""
    try:
        estadisticas = obtener_estadisticas_activos()
        return jsonify(estadisticas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@activos_bp.route("/api/<int:id>/toggle", methods=["PUT"])
def toggle_activo_route(id):
    """Activar o desactivar un activo"""
    try:
        activo = toggle_activo(id)
        estado = "activado" if activo.activo else "desactivado"
        return jsonify(
            {
                "success": True,
                "message": f"Activo {estado} exitosamente",
                "activo": activo.activo,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
