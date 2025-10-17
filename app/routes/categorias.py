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
    return render_template("inventario/categorias.html")


@categorias_web_bp.route("/estadisticas", methods=["GET"])
def obtener_estadisticas_web():
    """Obtiene estadísticas de categorías para web"""
    return CategoriasController.obtener_estadisticas()


@categorias_web_bp.route("/nueva")
def nueva():
    """Página para crear nueva categoría"""
    return render_template("inventario/categorias.html")


@categorias_web_bp.route("/<int:categoria_id>/editar")
def editar(categoria_id):
    """Página para editar categoría"""
    return render_template("inventario/categorias.html", categoria_id=categoria_id)
