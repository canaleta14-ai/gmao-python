"""
Configuración de documentación Swagger/OpenAPI para GMAO Sistema V2
==================================================================

Este módulo configura Flask-RESTX para generar documentación automática
de la API del sistema GMAO con interfaz Swagger UI interactiva.
"""

from flask_restx import Api, Resource, fields
from flask import Blueprint


def create_swagger_api():
    """
    Crea y configura la instancia principal de Flask-RESTX API

    Returns:
        Api: Instancia configurada de Flask-RESTX
    """

    # Crear blueprint para documentación
    api_v2_doc = Blueprint("api_v2_doc", __name__, url_prefix="/api/v2")

    # Configurar API con información del proyecto
    api = Api(
        api_v2_doc,
        version="2.0",
        title="GMAO Sistema - API V2",
        description="""
        # Sistema de Gestión de Mantenimiento y Activos (GMAO) - API V2
        
        ## 🚀 Características Principales
        
        Esta API V2 incluye optimizaciones avanzadas:
        
        - **📊 SQL Optimizado**: Índices y consultas mejoradas
        - **⚡ Sistema de Cache**: TTL y invalidación inteligente  
        - **📦 FIFO Optimizado**: Gestión eficiente de lotes e inventario
        - **📈 Métricas en tiempo real**: Monitoreo de performance
        - **🔄 Batch Processing**: Operaciones masivas optimizadas
        
        ## 🛠️ Arquitectura
        
        - **Framework**: Flask + SQLAlchemy + Flask-RESTX
        - **Base de datos**: PostgreSQL con índices optimizados
        - **Cache**: TTL con invalidación automática
        - **Monitoreo**: Métricas integradas de performance
        
        ## 📝 Autenticación
        
        Todos los endpoints requieren autenticación válida de sesión.
        
        ## 🔗 Endpoints Disponibles
        
        - **Inventario V2**: Gestión optimizada de artículos
        - **FIFO**: Control de lotes First In, First Out
        - **Performance**: Métricas y estadísticas del sistema
        - **Cache**: Gestión del sistema de caché
        
        ---
        *Documentación generada automáticamente - GMAO Sistema V2*
        """,
        doc="/docs/",
        license="MIT",
        contact="GMAO Team",
        contact_email="admin@gmao-system.com",
        tags=[
            {
                "name": "Inventario V2",
                "description": "Gestión optimizada de inventario con cache y SQL mejorado",
            },
            {
                "name": "FIFO",
                "description": "Control de lotes First In, First Out con batch processing",
            },
            {
                "name": "Performance",
                "description": "Métricas, estadísticas y monitoreo del sistema",
            },
            {"name": "Cache", "description": "Gestión del sistema de caché con TTL"},
            {
                "name": "Salud del Sistema",
                "description": "Health checks y diagnósticos",
            },
        ],
    )

    return api, api_v2_doc


# =============================================================================
# MODELOS SWAGGER PARA REQUESTS Y RESPONSES
# =============================================================================


def create_swagger_models(api):
    """
    Define todos los modelos Swagger para documentar requests y responses

    Args:
        api (Api): Instancia de Flask-RESTX API

    Returns:
        dict: Diccionario con todos los modelos Swagger
    """

    # Modelo base de respuesta exitosa
    success_model = api.model(
        "SuccessResponse",
        {
            "success": fields.Boolean(
                required=True, description="Indica si la operación fue exitosa"
            ),
            "message": fields.String(description="Mensaje descriptivo del resultado"),
            "timestamp": fields.String(
                description="Timestamp de la respuesta en formato ISO"
            ),
            "from_cache": fields.Boolean(
                description="Indica si la respuesta proviene del cache"
            ),
        },
    )

    # Modelo de error estándar
    error_model = api.model(
        "ErrorResponse",
        {
            "error": fields.String(required=True, description="Descripción del error"),
            "code": fields.Integer(description="Código de error interno"),
            "timestamp": fields.String(
                description="Timestamp del error en formato ISO"
            ),
            "details": fields.Raw(description="Detalles adicionales del error"),
        },
    )

    # Modelo de artículo de inventario
    inventario_model = api.model(
        "InventarioItem",
        {
            "id": fields.Integer(required=True, description="ID único del artículo"),
            "codigo_articulo": fields.String(
                required=True, description="Código único del artículo"
            ),
            "descripcion": fields.String(
                required=True, description="Descripción del artículo"
            ),
            "stock_actual": fields.Float(
                required=True, description="Cantidad actual en stock"
            ),
            "stock_minimo": fields.Float(description="Stock mínimo recomendado"),
            "stock_maximo": fields.Float(description="Stock máximo recomendado"),
            "precio_unitario": fields.Float(
                description="Precio unitario del artículo en EUR"
            ),
            "categoria_id": fields.Integer(description="ID de la categoría"),
            "categoria_nombre": fields.String(description="Nombre de la categoría"),
            "activo": fields.Boolean(description="Indica si el artículo está activo"),
            "ubicacion": fields.String(description="Ubicación física del artículo"),
            "proveedor": fields.String(description="Proveedor principal"),
            "unidad_medida": fields.String(
                description="Unidad de medida (kg, litros, piezas, etc.)"
            ),
            "fecha_creacion": fields.String(
                description="Fecha de creación en formato ISO"
            ),
            "fecha_modificacion": fields.String(
                description="Fecha de última modificación en formato ISO"
            ),
        },
    )

    # Modelo de lote FIFO
    lote_model = api.model(
        "LoteInventario",
        {
            "id": fields.Integer(required=True, description="ID único del lote"),
            "codigo_lote": fields.String(required=True, description="Código del lote"),
            "inventario_id": fields.Integer(
                required=True, description="ID del artículo de inventario"
            ),
            "cantidad_inicial": fields.Float(
                required=True, description="Cantidad inicial del lote"
            ),
            "cantidad_disponible": fields.Float(
                required=True, description="Cantidad disponible actual"
            ),
            "precio_unitario": fields.Float(
                required=True, description="Precio unitario del lote en EUR"
            ),
            "fecha_entrada": fields.String(
                required=True, description="Fecha de entrada en formato ISO"
            ),
            "fecha_vencimiento": fields.String(
                description="Fecha de vencimiento en formato ISO"
            ),
            "documento_referencia": fields.String(
                description="Documento de referencia"
            ),
            "proveedor": fields.String(description="Proveedor del lote"),
            "observaciones": fields.String(description="Observaciones adicionales"),
        },
    )

    # Modelo de movimiento de inventario
    movimiento_request = api.model(
        "MovimientoRequest",
        {
            "inventario_id": fields.Integer(
                required=True, description="ID del artículo de inventario"
            ),
            "tipo_movimiento": fields.String(
                required=True,
                description="Tipo de movimiento",
                enum=["entrada", "salida"],
                example="entrada",
            ),
            "cantidad": fields.Float(
                required=True, description="Cantidad del movimiento", example=10.5
            ),
            "precio_unitario": fields.Float(
                description="Precio unitario en EUR (requerido para entradas)",
                example=25.50,
            ),
            "codigo_lote": fields.String(
                description="Código opcional del lote", example="LOTE-2024-001"
            ),
            "fecha_vencimiento": fields.String(
                description="Fecha de vencimiento en formato ISO"
            ),
            "documento_referencia": fields.String(
                description="Documento de referencia", example="FACT-001"
            ),
            "proveedor": fields.String(
                description="Proveedor del artículo", example="ACME Corp"
            ),
            "observaciones": fields.String(description="Observaciones del movimiento"),
        },
    )

    # Modelo de respuesta de movimiento
    movimiento_response = api.model(
        "MovimientoResponse",
        {
            "success": fields.Boolean(
                required=True, description="Indica si el movimiento fue exitoso"
            ),
            "movimiento_id": fields.Integer(description="ID del movimiento creado"),
            "lote_id": fields.Integer(description="ID del lote afectado"),
            "stock_anterior": fields.Float(description="Stock antes del movimiento"),
            "stock_nuevo": fields.Float(description="Stock después del movimiento"),
            "mensaje": fields.String(description="Mensaje descriptivo"),
            "timestamp": fields.String(description="Timestamp del movimiento"),
            "from_cache": fields.Boolean(
                description="Indica si la respuesta usa cache"
            ),
        },
    )

    # Modelo de estadísticas del sistema
    estadisticas_model = api.model(
        "EstadisticasResponse",
        {
            "total_articulos": fields.Integer(
                description="Total de artículos en el sistema"
            ),
            "total_categorias": fields.Integer(description="Total de categorías"),
            "valor_total_inventario": fields.Float(
                description="Valor total del inventario"
            ),
            "articulos_stock_bajo": fields.Integer(
                description="Artículos con stock bajo"
            ),
            "articulos_sin_stock": fields.Integer(description="Artículos sin stock"),
            "total_lotes": fields.Integer(description="Total de lotes en el sistema"),
            "lotes_proximos_vencer": fields.Integer(
                description="Lotes próximos a vencer"
            ),
            "from_cache": fields.Boolean(
                description="Indica si la respuesta proviene del cache"
            ),
            "tiempo_respuesta_ms": fields.Float(
                description="Tiempo de respuesta en milisegundos"
            ),
            "timestamp": fields.String(description="Timestamp de la consulta"),
        },
    )

    # Modelo de métricas de performance
    performance_model = api.model(
        "PerformanceMetrics",
        {
            "endpoint": fields.String(description="Nombre del endpoint"),
            "total_requests": fields.Integer(description="Total de requests"),
            "avg_response_time_ms": fields.Float(
                description="Tiempo promedio de respuesta en ms"
            ),
            "min_response_time_ms": fields.Float(
                description="Tiempo mínimo de respuesta en ms"
            ),
            "max_response_time_ms": fields.Float(
                description="Tiempo máximo de respuesta en ms"
            ),
            "cache_hits": fields.Integer(description="Número de cache hits"),
            "cache_misses": fields.Integer(description="Número de cache misses"),
            "cache_hit_rate": fields.Float(description="Tasa de cache hits (0-1)"),
            "error_count": fields.Integer(description="Número de errores"),
            "last_request": fields.String(description="Timestamp del último request"),
        },
    )

    # Modelo de health check
    health_model = api.model(
        "HealthResponse",
        {
            "status": fields.String(
                required=True, description="Estado general del sistema"
            ),
            "timestamp": fields.String(
                required=True, description="Timestamp del health check"
            ),
            "services": fields.Raw(description="Estado de servicios individuales"),
            "version": fields.String(description="Versión de la API"),
            "uptime_seconds": fields.Float(
                description="Tiempo de actividad en segundos"
            ),
        },
    )

    # Modelo de respuesta de lista de inventario
    inventario_list_response = api.model(
        "InventarioListResponse",
        {
            "items": fields.List(
                fields.Nested(inventario_model), description="Lista de artículos"
            ),
            "total": fields.Integer(description="Total de artículos"),
            "page": fields.Integer(description="Página actual"),
            "per_page": fields.Integer(description="Items por página"),
            "pages": fields.Integer(description="Total de páginas"),
            "from_cache": fields.Boolean(
                description="Indica si la respuesta proviene del cache"
            ),
            "timestamp": fields.String(description="Timestamp de la consulta"),
        },
    )

    # Modelo de respuesta de lotes
    lotes_response = api.model(
        "LotesResponse",
        {
            "inventario_id": fields.Integer(
                description="ID del artículo de inventario"
            ),
            "total_lotes": fields.Integer(description="Total de lotes"),
            "total_disponible": fields.Float(description="Cantidad total disponible"),
            "lotes": fields.List(
                fields.Nested(lote_model), description="Lista de lotes"
            ),
            "from_cache": fields.Boolean(
                description="Indica si la respuesta proviene del cache"
            ),
            "timestamp": fields.String(description="Timestamp de la consulta"),
        },
    )

    return {
        "success": success_model,
        "error": error_model,
        "inventario": inventario_model,
        "lote": lote_model,
        "movimiento_request": movimiento_request,
        "movimiento_response": movimiento_response,
        "estadisticas": estadisticas_model,
        "performance": performance_model,
        "health": health_model,
        "inventario_list": inventario_list_response,
        "lotes_response": lotes_response,
    }


# =============================================================================
# DECORADORES SWAGGER PERSONALIZADOS
# =============================================================================


def swagger_response(api, success_model=None, error_model=None, success_code=200):
    """
    Decorador personalizado para documentar responses de endpoints

    Args:
        api: Instancia de Flask-RESTX API
        success_model: Modelo Swagger para respuesta exitosa
        error_model: Modelo Swagger para respuesta de error
        success_code: Código HTTP de éxito (default: 200)
    """

    def decorator(f):
        if success_model:
            f = api.response(success_code, "Éxito", success_model)(f)
        if error_model:
            f = api.response(400, "Error de validación", error_model)(f)
            f = api.response(404, "Recurso no encontrado", error_model)(f)
            f = api.response(500, "Error interno del servidor", error_model)(f)
        return f

    return decorator
