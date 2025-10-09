from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from app.controllers.inventario_controller_simple import (
    obtener_estadisticas_inventario,
    listar_articulos_avanzado,
    crear_articulo_simple,
)

inventario_bp = Blueprint("inventario", __name__, url_prefix="/inventario")


@inventario_bp.route("/")
def inventario_page():
    """Página principal de inventario"""
    return render_template("inventario/inventario.html", section="inventario")


@inventario_bp.route("/api/estadisticas", methods=["GET"])
@login_required
def obtener_estadisticas():
    """API para obtener estadísticas del inventario"""
    try:
        stats = obtener_estadisticas_inventario()
        if not isinstance(stats, dict):
            stats = {}
        for key, default in [
            ("total_articulos", 0),
            ("valor_total_stock", 0),
            ("articulos_bajo_minimo", 0),
            ("articulos_criticos", 0),
        ]:
            stats.setdefault(key, default)
        return jsonify(stats), 200
    except Exception as e:
        fallback = {
            "total_articulos": 0,
            "valor_total_stock": 0,
            "articulos_bajo_minimo": 0,
            "articulos_criticos": 0,
        }
        return jsonify({"success": False, "error": str(e), **fallback}), 200


@inventario_bp.route("/api/articulos", methods=["GET"])
@login_required
def obtener_articulos():
    """API para listar artículos con filtros avanzados"""
    try:
        filtros = {}
        # Filtros de búsqueda
        if "codigo" in request.args:
            filtros["codigo"] = request.args["codigo"]
        if "descripcion" in request.args:
            filtros["descripcion"] = request.args["descripcion"]
        if "categoria" in request.args:
            filtros["categoria"] = request.args["categoria"]
        if "ubicacion" in request.args:
            filtros["ubicacion"] = request.args["ubicacion"]
        if "bajo_minimo" in request.args:
            filtros["bajo_minimo"] = (
                request.args.get("bajo_minimo", "").lower() == "true"
            )
        if "critico" in request.args:
            filtros["critico"] = request.args.get("critico", "").lower() == "true"

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        articulos, total = listar_articulos_avanzado(filtros, page, per_page)

        return jsonify(
            {
                "total": total,
                "page": page,
                "per_page": per_page,
                "articulos": [
                    {
                        "id": a.id,
                        "codigo": a.codigo,
                        "descripcion": a.descripcion,
                        "categoria": a.categoria,
                        "stock_actual": float(a.stock_actual) if a.stock_actual else 0,
                        "stock_minimo": float(a.stock_minimo) if a.stock_minimo else 0,
                        "stock_maximo": float(a.stock_maximo) if a.stock_maximo else 0,
                        "ubicacion": a.ubicacion,
                        "precio_unitario": (
                            float(a.precio_unitario) if a.precio_unitario else 0
                        ),
                        "precio_promedio": (
                            float(a.precio_promedio) if a.precio_promedio else 0
                        ),
                        "unidad_medida": a.unidad_medida,
                        "proveedor_principal": a.proveedor_principal,
                        "cuenta_contable_compra": a.cuenta_contable_compra,
                        "grupo_contable": a.grupo_contable,
                        "critico": a.critico,
                        "valor_stock": a.valor_stock,
                        "necesita_reposicion": a.necesita_reposicion,
                        "activo": a.activo,
                    }
                    for a in articulos
                ],
            }
        )
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": "Error al obtener artículos"}), 500


@inventario_bp.route("/api/articulos", methods=["POST"])
@login_required
def crear_articulo():
    """API para crear un nuevo artículo"""
    try:
        data = request.get_json()
        articulo = crear_articulo_simple(data)
        return jsonify(
            {
                "success": True,
                "message": "Artículo creado exitosamente",
                "articulo": {
                    "id": articulo.id,
                    "codigo": articulo.codigo,
                    "descripcion": articulo.descripcion,
                },
            }
        )
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": "Error al crear artículo"}), 500


@inventario_bp.route("/conteos")
def conteos_page():
    """Página de conteos de inventario"""
    return render_template("inventario/conteos.html", section="inventario")
