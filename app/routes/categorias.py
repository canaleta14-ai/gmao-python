from flask import Blueprint, render_template, request
from app.controllers.categorias_controller import CategoriasController

categorias_bp = Blueprint("categorias", __name__, url_prefix="/api/categorias")


# API Routes
@categorias_bp.route("/", methods=["GET"])
def obtener_categorias():
    """Obtiene todas las categorías"""
    return CategoriasController.obtener_todas()


@categorias_bp.route("/", methods=["POST"])
def crear_categoria():
    """Crea una nueva categoría"""
    return CategoriasController.crear()


@categorias_bp.route("/<int:categoria_id>", methods=["PUT"])
def actualizar_categoria(categoria_id):
    """Actualiza una categoría existente"""
    return CategoriasController.actualizar(categoria_id)


@categorias_bp.route("/<int:categoria_id>", methods=["DELETE"])
def eliminar_categoria(categoria_id):
    """Elimina una categoría"""
    return CategoriasController.eliminar(categoria_id)


@categorias_bp.route("/<int:categoria_id>/codigo", methods=["GET"])
def generar_codigo(categoria_id):
    """Genera el próximo código para una categoría"""
    return CategoriasController.generar_codigo(categoria_id)


@categorias_bp.route("/estadisticas", methods=["GET"])
def obtener_estadisticas():
    """Obtiene estadísticas de categorías"""
    return CategoriasController.obtener_estadisticas()


# Web Routes (si necesitas vistas HTML)
categorias_web_bp = Blueprint("categorias_web", __name__, url_prefix="/categorias")


@categorias_web_bp.route("/")
def index():
    """Página principal de gestión de categorías"""
    # Respuesta HTML directa para evitar error de template
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Categorías - GMAO</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container-fluid p-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1 class="h3 mb-0 text-gray-800">
                    <i class="fas fa-tags mr-2"></i>Gestión de Categorías
                </h1>
                <a href="/" class="btn btn-secondary">
                    <i class="fas fa-home mr-2"></i>Volver al Dashboard
                </a>
            </div>
            
            <div class="card shadow mb-4">
                <div class="card-header py-3">
                    <h6 class="m-0 font-weight-bold text-primary">Módulo de Categorías</h6>
                </div>
                <div class="card-body">
                    <p><strong>Estado:</strong> <span class="badge badge-success">Funcionando</span></p>
                    <p><strong>Descripción:</strong> Sistema de gestión de categorías para inventario y activos.</p>
                    <p><strong>Funcionalidades:</strong></p>
                    <ul>
                        <li>Crear, editar y eliminar categorías</li>
                        <li>Gestión de códigos y clasificaciones</li>
                        <li>Integración con inventario y activos</li>
                        <li>API de estadísticas disponible</li>
                    </ul>
                    
                    <div class="mt-4">
                        <h6>Enlaces Útiles:</h6>
                        <a href="/categorias/estadisticas" class="btn btn-info btn-sm mr-2">
                            <i class="fas fa-chart-bar mr-1"></i>Ver Estadísticas
                        </a>
                        <a href="/api/categorias" class="btn btn-primary btn-sm">
                            <i class="fas fa-code mr-1"></i>API Categorías
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="text-center">
                <small class="text-muted">GMAO Sistema - Gestión de Mantenimiento</small>
            </div>
        </div>
        
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return html_content


@categorias_web_bp.route("/estadisticas", methods=["GET"])
def obtener_estadisticas_web():
    """Obtiene estadísticas de categorías para web"""
    return CategoriasController.obtener_estadisticas()


@categorias_web_bp.route("/nueva")
def nueva():
    """Página para crear nueva categoría"""
    return render_template("inventario/categoria_form.html")


@categorias_web_bp.route("/<int:categoria_id>/editar")
def editar(categoria_id):
    """Página para editar categoría"""
    return render_template("inventario/categoria_form.html", categoria_id=categoria_id)
