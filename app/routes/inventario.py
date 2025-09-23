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
        return jsonify(stats)
    except Exception as e:
        return (
            jsonify({"success": False, "error": "Error al obtener estadísticas"}),
            500,
        )


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
