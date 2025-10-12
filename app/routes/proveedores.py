from flask import Blueprint, request, jsonify, render_template, Response
from flask_login import login_required
from app.controllers.proveedores_controller import (
    listar_proveedores,
    listar_proveedores_paginado,
    crear_proveedor,
    actualizar_proveedor,
    eliminar_proveedor,
    obtener_proveedor,
    exportar_proveedores_csv,
    validar_nif,
    obtener_estadisticas_proveedores,
    toggle_proveedor,
)

proveedores_bp = Blueprint("proveedores", __name__, url_prefix="/proveedores")


@proveedores_bp.route("/", methods=["GET", "POST"])
@login_required
def proveedores_page():
    if request.method == "GET":
        """Página principal de proveedores"""
        try:
            return render_template(
                "proveedores/proveedores.html", section="proveedores"
            )
        except Exception:
            html = """
            <!DOCTYPE html>
            <html lang=\"es\">
            <head><meta charset=\"utf-8\"><title>Proveedores</title></head>
            <body>
                <h1>Proveedores</h1>
                <p>La página de proveedores no pudo renderizarse completamente, pero el sistema está operativo.</p>
            </body>
            </html>
            """
            return Response(html, mimetype="text/html")
    elif request.method == "POST":
        try:
            data = request.get_json()
            nuevo_proveedor = crear_proveedor(data)
            return jsonify(
                {
                    "success": True,
                    "message": "Proveedor creado exitosamente",
                    "id": nuevo_proveedor.id,
                }
            )
        except ValueError as e:
            return jsonify({"success": False, "message": str(e)}), 400
        except Exception as e:
            return (
                jsonify({"success": False, "message": "Error interno del servidor"}),
                500,
            )


@proveedores_bp.route("/api", methods=["GET"])
@login_required
def proveedores_list_api():
    """API para listar proveedores con soporte para filtros de búsqueda y paginación"""
    try:
        # Parámetros de paginación
        page = request.args.get("page", type=int)
        per_page = request.args.get("per_page", type=int)
        format_type = (request.args.get("format", "") or "").lower()
        q = request.args.get("q")

        if page is not None:
            # Usar paginación
            per_page = per_page or 10
            resultado = listar_proveedores_paginado(page, per_page, q)
            return jsonify(resultado)
        else:
            # Usar listado tradicional sin paginación
            filtros = {}
            # Recoger parámetros de filtro de la URL
            for param in ["nombre", "nif", "contacto", "q", "limit"]:
                if param in request.args:
                    filtros[param] = request.args[param]
            lista = listar_proveedores(filtros if filtros else None)
            if format_type in ("object", "dict", "default"):
                return jsonify({"success": True, "items": lista, "total": len(lista)})
            return jsonify(lista)
    except Exception as e:
        return jsonify({"error": "Error al obtener proveedores"}), 500


@proveedores_bp.route("/api/<int:id>", methods=["GET", "PUT", "DELETE"])
@login_required
def proveedor_detail(id):
    try:
        if request.method == "GET":
            proveedor = obtener_proveedor(id)
            return jsonify(proveedor)

        elif request.method == "PUT":
            data = request.get_json()
            proveedor_actualizado = actualizar_proveedor(id, data)
            return jsonify(
                {
                    "success": True,
                    "message": "Proveedor actualizado exitosamente",
                    "id": proveedor_actualizado.id,
                }
            )

        elif request.method == "DELETE":
            eliminar_proveedor(id)
            return jsonify(
                {"success": True, "message": "Proveedor eliminado exitosamente"}
            )

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500


@proveedores_bp.route("/validar-nif", methods=["POST"])
def validar_nif_route():
    """Valida que un NIF no esté duplicado"""
    try:
        data = request.get_json()
        if not data or "nif" not in data:
            return jsonify({"error": "NIF es requerido"}), 400

        resultado = validar_nif(data["nif"])
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@proveedores_bp.route("/exportar-csv", methods=["GET"])
def exportar_csv():
    """Exporta todos los proveedores a Excel"""
    try:
        excel_data = exportar_proveedores_csv()

        response = Response(
            excel_data,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-disposition": "attachment; filename=proveedores.xlsx"},
        )
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@proveedores_bp.route("/select", methods=["GET"])
def proveedores_select():
    """API optimizada para select/dropdown de proveedores"""
    try:
        proveedores = listar_proveedores()
        # Formato simplificado para selects
        return jsonify(
            [
                {"id": p["id"], "nombre": p["nombre"], "nif": p["nif"]}
                for p in proveedores
            ]
        )
    except Exception as e:
        return jsonify({"error": "Error al obtener proveedores"}), 500


@proveedores_bp.route("/api/estadisticas", methods=["GET"])
@login_required
def estadisticas_proveedores():
    """Obtener estadísticas de proveedores"""
    try:
        estadisticas = obtener_estadisticas_proveedores()
        if not isinstance(estadisticas, dict):
            estadisticas = {}
        # Asegurar claves mínimas esperadas por frontend
        for key in [
            "total_proveedores",
            "proveedores_activos",
            "proveedores_pendientes",
            "proveedores_inactivos",
        ]:
            estadisticas.setdefault(key, 0)
        return jsonify(estadisticas), 200
    except Exception as e:
        # Retornar error 500 para consistencia con el resto del sistema
        return jsonify({"success": False, "error": str(e)}), 500


@proveedores_bp.route("/api/<int:id>/toggle", methods=["PUT"])
@login_required
def toggle_proveedor_route(id):
    """Activar o desactivar un proveedor"""
    try:
        proveedor = toggle_proveedor(id)
        estado = "activado" if proveedor.activo else "desactivado"
        return jsonify(
            {
                "success": True,
                "message": f"Proveedor {estado} exitosamente",
                "activo": proveedor.activo,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
