from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from functools import wraps
from app.controllers.inventario_controller_simple import (
    obtener_estadisticas_inventario,
    listar_articulos_avanzado,
    crear_articulo_simple,
    exportar_inventario_csv,
    registrar_movimiento_inventario,
    obtener_movimientos_articulo,
    obtener_movimientos_generales,
    editar_articulo_simple,
)


def api_login_required(f):
    """Decorador para rutas de API que devuelve JSON en lugar de redirigir"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        return f(*args, **kwargs)

    return decorated_function


inventario_bp = Blueprint("inventario", __name__, url_prefix="/inventario")


@inventario_bp.route("/")
def inventario_page():
    """Página principal de inventario"""
    return render_template("inventario/inventario.html", section="inventario")


@inventario_bp.route("/api/estadisticas", methods=["GET"])
@api_login_required
def obtener_estadisticas():
    """API para obtener estadísticas del inventario"""
    try:
        stats = obtener_estadisticas_inventario()
        return jsonify(stats)
    except Exception as e:
        return (
            jsonify({"success": False, "error": "Error al obtener estadísticas"}),
            500,
        )


@inventario_bp.route("/api/articulos", methods=["GET"])
@api_login_required
def obtener_articulos():
    """API para listar artículos con filtros avanzados"""
    try:
        filtros = {}

        # Búsqueda general (para autocompletado)
        if "q" in request.args:
            search_term = request.args["q"]
            # Aplicar búsqueda general en código, descripción y categoría
            filtros["busqueda_general"] = search_term

        # Filtros específicos
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


@inventario_bp.route("/exportar-csv", methods=["GET"])
@login_required
def exportar_csv():
    """Exporta los artículos del inventario a CSV"""
    try:
        from flask import Response

        csv_data = exportar_inventario_csv()

        response = Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=inventario.csv"},
        )
        return response
    except Exception as e:
        return jsonify({"success": False, "error": "Error al exportar CSV"}), 500


@inventario_bp.route("/api/articulos", methods=["POST"])
@api_login_required
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


@inventario_bp.route("/test-spinner")
def test_spinner():
    """Página de prueba para el spinner"""
    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Spinner</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container mt-5">
        <h2>Test del Spinner</h2>
        
        <div class="table-responsive mt-4">
            <table class="table">
                <thead>
                    <tr>
                        <th>Código</th>
                        <th>Descripción</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody id="test-tbody">
                    <!-- Spinner de prueba -->
                    <tr id="loading-row">
                        <td colspan="3" class="text-center py-4">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Cargando...</span>
                            </div>
                            <p class="mt-2 text-muted">Cargando artículos...</p>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <button class="btn btn-primary" onclick="testSpinner()">Simular Carga</button>
        <button class="btn btn-danger" onclick="clearSpinner()">Limpiar</button>
    </div>

    <script>
        function testSpinner() {
            const tbody = document.getElementById('test-tbody');
            tbody.innerHTML = `
                <tr id="loading-row">
                    <td colspan="3" class="text-center py-4">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Cargando...</span>
                        </div>
                        <p class="mt-2 text-muted">Cargando artículos...</p>
                    </td>
                </tr>
            `;
            
            // Simular carga de 3 segundos
            setTimeout(() => {
                tbody.innerHTML = `
                    <tr>
                        <td>TEST001</td>
                        <td>Artículo de prueba</td>
                        <td><span class="badge bg-success">Activo</span></td>
                    </tr>
                `;
            }, 3000);
        }
        
        function clearSpinner() {
            const tbody = document.getElementById('test-tbody');
            tbody.innerHTML = `
                <tr>
                    <td colspan="3" class="text-center py-4">
                        <div class="text-muted">Sin datos</div>
                    </td>
                </tr>
            `;
        }
    </script>
</body>
</html>"""


@inventario_bp.route("/reportes")
def reportes_page():
    """Página de reportes de inventario"""
    return render_template("inventario/reportes.html", section="inventario")


# Rutas de API para movimientos de inventario
@inventario_bp.route("/api/movimientos", methods=["POST"])
@api_login_required
def registrar_movimiento():
    """API para registrar un nuevo movimiento de inventario"""
    try:
        data = request.get_json()
        movimiento = registrar_movimiento_inventario(data)
        return jsonify(
            {
                "success": True,
                "message": "Movimiento registrado exitosamente",
                "movimiento": {
                    "id": movimiento.id,
                    "tipo": movimiento.tipo,
                    "cantidad": movimiento.cantidad,
                    "fecha": (
                        movimiento.fecha.strftime("%d/%m/%Y %H:%M")
                        if movimiento.fecha
                        else ""
                    ),
                },
            }
        )
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return (
            jsonify({"success": False, "error": "Error al registrar movimiento"}),
            500,
        )


@inventario_bp.route("/api/articulos/<int:articulo_id>/movimientos", methods=["GET"])
@api_login_required
def obtener_historial_articulo(articulo_id):
    """API para obtener historial de movimientos de un artículo"""
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        data = obtener_movimientos_articulo(articulo_id, page, per_page)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": False, "error": "Error al obtener historial"}), 500


@inventario_bp.route("/api/movimientos", methods=["GET"])
@api_login_required
def obtener_movimientos():
    """API para obtener vista general de movimientos"""
    try:
        filtros = {}
        if "tipo" in request.args:
            filtros["tipo"] = request.args["tipo"]
        if "fecha_desde" in request.args:
            filtros["fecha_desde"] = request.args["fecha_desde"]
        if "fecha_hasta" in request.args:
            filtros["fecha_hasta"] = request.args["fecha_hasta"]
        if "usuario_id" in request.args:
            filtros["usuario_id"] = request.args["usuario_id"]

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        data = obtener_movimientos_generales(filtros, page, per_page)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": False, "error": "Error al obtener movimientos"}), 500


# Ruta para editar artículo
@inventario_bp.route("/api/articulos/<int:articulo_id>", methods=["PUT"])
@api_login_required
def editar_articulo(articulo_id):
    """API para editar un artículo existente"""
    try:
        data = request.get_json()
        articulo = editar_articulo_simple(articulo_id, data)
        return jsonify(
            {
                "success": True,
                "message": "Artículo actualizado exitosamente",
                "articulo": {
                    "id": articulo.id,
                    "codigo": articulo.codigo,
                    "descripcion": articulo.descripcion,
                    "categoria": articulo.categoria,
                    "ubicacion": articulo.ubicacion,
                    "stock_actual": articulo.stock_actual,
                    "activo": articulo.activo,
                },
            }
        )
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": "Error al editar artículo"}), 500


# Ruta para obtener un artículo individual
@inventario_bp.route("/api/articulos/<int:articulo_id>", methods=["GET"])
@api_login_required
def obtener_articulo(articulo_id):
    """API para obtener un artículo individual"""
    try:
        from app.models.inventario import Inventario

        articulo = Inventario.query.get(articulo_id)
        if not articulo:
            return jsonify({"success": False, "error": "Artículo no encontrado"}), 404

        return jsonify(
            {
                "id": articulo.id,
                "codigo": articulo.codigo,
                "descripcion": articulo.descripcion,
                "categoria": articulo.categoria,
                "subcategoria": articulo.subcategoria,
                "ubicacion": articulo.ubicacion,
                "stock_actual": articulo.stock_actual,
                "stock_minimo": articulo.stock_minimo,
                "stock_maximo": articulo.stock_maximo,
                "unidad_medida": articulo.unidad_medida,
                "precio_unitario": articulo.precio_unitario,
                "proveedor_principal": articulo.proveedor_principal,
                "cuenta_contable_compra": articulo.cuenta_contable_compra,
                "grupo_contable": articulo.grupo_contable,
                "critico": articulo.critico,
                "activo": articulo.activo,
                "observaciones": articulo.observaciones,
                "fecha_creacion": (
                    articulo.fecha_creacion.strftime("%d/%m/%Y")
                    if articulo.fecha_creacion
                    else ""
                ),
                "fecha_actualizacion": (
                    articulo.fecha_actualizacion.strftime("%d/%m/%Y")
                    if articulo.fecha_actualizacion
                    else ""
                ),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": "Error al obtener artículo"}), 500
