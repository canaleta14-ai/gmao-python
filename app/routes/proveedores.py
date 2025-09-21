from flask import Blueprint, request, jsonify, render_template, Response
from app.controllers.proveedores_controller import (
    listar_proveedores,
    crear_proveedor,
    actualizar_proveedor,
    eliminar_proveedor,
    obtener_proveedor,
    exportar_proveedores_csv,
    validar_nif,
)

proveedores_bp = Blueprint("proveedores", __name__, url_prefix="/proveedores")


@proveedores_bp.route("/", methods=["GET", "POST"])
def proveedores_page():
    if request.method == "GET":
        """Página principal de proveedores"""
        return render_template("proveedores/proveedores.html", section="proveedores")
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
def proveedores_list_api():
    """API para listar proveedores con soporte para filtros de búsqueda"""
    try:
        filtros = {}

        # Recoger parámetros de filtro de la URL
        for param in ["nombre", "nif", "contacto", "q", "limit"]:
            if param in request.args:
                filtros[param] = request.args[param]

        return jsonify(listar_proveedores(filtros if filtros else None))
    except Exception as e:
        return jsonify({"error": "Error al obtener proveedores"}), 500


@proveedores_bp.route("/api/<int:id>", methods=["GET", "PUT", "DELETE"])
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
    """Exporta todos los proveedores a CSV"""
    try:
        csv_data = exportar_proveedores_csv()

        response = Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=proveedores.csv"},
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
