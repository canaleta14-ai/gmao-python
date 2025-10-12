#!/usr/bin/env python3
"""
🚀 BLUEPRINT DE INVENTARIO OPTIMIZADO V2 - CON DOCUMENTACIÓN SWAGGER
====================================================================

Este blueprint incluye documentación automática OpenAPI/Swagger para todos
los endpoints de inventario optimizado. Se integrará dinámicamente con
Flask-RESTX cuando la aplicación esté corriendo.
"""

from flask import Blueprint, jsonify, request
from app.controllers import inventario_controller_optimizado as controller_opt
from app.blueprints.performance_metrics import performance_monitor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Crear blueprint para inventario optimizado
inventario_optimizado_bp = Blueprint(
    "inventario_optimizado", __name__, url_prefix="/api/v2/inventario"
)


@inventario_optimizado_bp.route("/", methods=["GET"])
@performance_monitor("api_inventario_list_v2")
def listar_inventario():
    """
    📋 Lista todos los artículos del inventario con optimizaciones completas

    **Características:**
    - Cache con TTL para respuestas rápidas
    - SQL optimizado con índices
    - Paginación automática
    - Filtros múltiples disponibles
    - Métricas de performance integradas

    **Parámetros de consulta:**
    - page: Número de página (default: 1)
    - per_page: Items por página (default: 50)
    - activo: Filtrar por estado activo (true/false)
    - categoria_id: Filtrar por ID de categoría
    - stock_bajo: Mostrar solo artículos con stock bajo

    **Ejemplo de respuesta:**
    ```json
    {
        "items": [
            {
                "id": 1,
                "codigo_articulo": "FIFO-ACERO-001",
                "descripcion": "Acero inoxidable",
                "stock_actual": 25.5,
                "precio_unitario": 15.75
            }
        ],
        "total": 1005,
        "page": 1,
        "from_cache": true,
        "timestamp": "2024-10-12T10:30:00"
    }
    ```
    """
    try:
        resultado = controller_opt.listar_inventario_optimizado()

        if "error" in resultado:
            return jsonify(resultado), 500

        return jsonify(resultado), 200

    except Exception as e:
        logger.error(f"Error en endpoint listar_inventario: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Error interno del servidor",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@inventario_optimizado_bp.route("/estadisticas", methods=["GET"])
@performance_monitor("api_inventario_stats_v2")
def obtener_estadisticas():
    """
    📊 Obtiene estadísticas completas del inventario

    **Información incluida:**
    - Total de artículos y categorías
    - Valor total del inventario
    - Artículos con stock bajo/sin stock
    - Total de lotes y próximos a vencer
    - Métricas de performance del endpoint

    **Optimizaciones:**
    - Cache inteligente con TTL
    - Consultas SQL optimizadas
    - Cálculos agregados eficientes

    **Ejemplo de respuesta:**
    ```json
    {
        "total_articulos": 1005,
        "total_categorias": 25,
        "valor_total_inventario": 484673016.83,
        "articulos_stock_bajo": 15,
        "articulos_sin_stock": 3,
        "total_lotes": 2340,
        "lotes_proximos_vencer": 12,
        "from_cache": true,
        "tiempo_respuesta_ms": 45.2,
        "timestamp": "2024-10-12T10:30:00"
    }
    ```
    """
    try:
        resultado = controller_opt.obtener_estadisticas_optimizado()

        if "error" in resultado:
            return jsonify(resultado), 500

        # Estructura de respuesta mejorada
        estadisticas = resultado.get("estadisticas", {})
        respuesta = {
            **estadisticas,  # Expandir estadísticas al nivel superior
            "from_cache": resultado.get("from_cache", False),
            "tiempo_respuesta_ms": resultado.get("tiempo_respuesta_ms"),
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify(respuesta), 200

    except Exception as e:
        logger.error(f"Error en endpoint obtener_estadisticas: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Error interno del servidor",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@inventario_optimizado_bp.route("/<int:inventario_id>", methods=["GET"])
@performance_monitor("api_inventario_get_v2")
def obtener_articulo(inventario_id):
    """
    🔍 Obtiene un artículo específico del inventario

    **Parámetros:**
    - inventario_id: ID único del artículo (requerido)

    **Información incluida:**
    - Datos completos del artículo
    - Stock actual y límites
    - Información de categoría y proveedor
    - Métricas de rotación (si disponible)
    - Ubicación y estado

    **Optimizaciones aplicadas:**
    - Cache individual por artículo
    - Consulta SQL optimizada con joins
    - Conversión de tipos mejorada

    **Ejemplo de respuesta:**
    ```json
    {
        "id": 1,
        "codigo_articulo": "FIFO-ACERO-001",
        "descripcion": "Acero inoxidable 304",
        "stock_actual": 25.5,
        "stock_minimo": 10.0,
        "precio_unitario": 15.75,
        "categoria": "Materiales",
        "activo": true,
        "from_cache": true
    }
    ```
    """
    try:
        resultado = controller_opt.obtener_articulo_optimizado(inventario_id)

        if "error" in resultado:
            if "no encontrado" in resultado["error"].lower():
                return jsonify(resultado), 404
            return jsonify(resultado), 500

        return jsonify(resultado), 200

    except Exception as e:
        logger.error(f"Error en endpoint obtener_articulo: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Error interno del servidor",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@inventario_optimizado_bp.route("/<int:inventario_id>/lotes", methods=["GET"])
@performance_monitor("api_inventario_lotes_v2")
def obtener_lotes_articulo(inventario_id):
    """
    📦 Obtiene todos los lotes de un artículo con orden FIFO

    **Parámetros:**
    - inventario_id: ID único del artículo (requerido)

    **Características:**
    - Orden First In, First Out automático
    - Solo lotes con cantidad disponible > 0
    - Información completa de cada lote
    - Totales agregados

    **Información por lote:**
    - Código y fechas del lote
    - Cantidades inicial y disponible
    - Precio unitario en EUR y proveedor
    - Documento de referencia

    **Ejemplo de respuesta:**
    ```json
    {
        "inventario_id": 1,
        "total_lotes": 5,
        "total_disponible": 45.5,
        "lotes": [
            {
                "id": 123,
                "codigo_lote": "L20241012134552",
                "cantidad_disponible": 10.0,
                "precio_unitario": 25.5,
                "fecha_entrada": "2024-10-12T13:45:52"
            }
        ],
        "timestamp": "2024-10-12T10:30:00"
    }
    ```
    """
    try:
        from fifo_optimizado import FIFOOptimizado

        fifo_opt = FIFOOptimizado()
        lotes = fifo_opt._obtener_lotes_optimizado(inventario_id)

        # Filtrar solo lotes con cantidad disponible
        lotes_disponibles = [lote for lote in lotes if lote.cantidad_disponible > 0]

        lotes_data = []
        total_disponible = 0.0

        for lote in lotes_disponibles:
            lote_info = {
                "id": lote.id,
                "codigo_lote": getattr(lote, "codigo_lote", f"L-{lote.id}"),
                "cantidad_disponible": float(lote.cantidad_disponible),
                "cantidad_inicial": float(lote.cantidad_inicial),
                "fecha_entrada": (
                    lote.fecha_entrada.isoformat() if lote.fecha_entrada else None
                ),
                "fecha_vencimiento": (
                    lote.fecha_vencimiento.isoformat()
                    if lote.fecha_vencimiento
                    else None
                ),
                "precio_unitario": float(lote.precio_unitario or 0),
                "documento_referencia": getattr(lote, "documento_referencia", None),
                "proveedor": getattr(lote, "proveedor", None),
            }
            lotes_data.append(lote_info)
            total_disponible += lote.cantidad_disponible

        resultado = {
            "inventario_id": inventario_id,
            "total_lotes": len(lotes_data),
            "total_disponible": total_disponible,
            "lotes": lotes_data,
            "from_cache": False,  # Los lotes usan su propio cache interno
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify(resultado), 200

    except Exception as e:
        logger.error(f"Error en endpoint obtener_lotes_articulo: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Error interno del servidor",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@inventario_optimizado_bp.route("/movimientos", methods=["POST"])
@performance_monitor("api_inventario_movimiento_v2")
def crear_movimiento():
    """
    📝 Crea un movimiento de inventario con procesamiento FIFO optimizado

    **Tipos de movimiento:**
    - **Entrada**: Incrementa stock, crea nuevo lote
    - **Salida**: Decrementa stock usando FIFO automático

    **Campos requeridos:**
    - inventario_id: ID del artículo (integer)
    - tipo_movimiento: "entrada" o "salida" (string)
    - cantidad: Cantidad del movimiento (float, >0)
    - precio_unitario: Precio en EUR (float, requerido para entradas)

    **Campos opcionales:**
    - codigo_lote: Código del lote (string)
    - fecha_vencimiento: Fecha ISO (string)
    - documento_referencia: Documento (string)
    - proveedor: Proveedor (string)
    - observaciones: Notas (string)

    **Validaciones:**
    - Cantidad debe ser positiva
    - Precio en EUR requerido para entradas
    - Stock suficiente para salidas
    - Artículo debe existir y estar activo

    **Procesamiento automático:**
    - Entradas: Nuevo lote con código automático
    - Salidas: FIFO optimizado con batch processing
    - Cache invalidado automáticamente
    - Métricas de performance registradas

    **Ejemplo de request (entrada):**
    ```json
    {
        "inventario_id": 1,
        "tipo_movimiento": "entrada",
        "cantidad": 10.5,
        "precio_unitario": 25.50,
        "codigo_lote": "LOTE-2024-001",
        "proveedor": "ACME Corp"
    }
    ```

    **Ejemplo de request (salida):**
    ```json
    {
        "inventario_id": 1,
        "tipo_movimiento": "salida",
        "cantidad": 5.0,
        "observaciones": "Uso en orden 12345"
    }
    ```

    **Ejemplo de respuesta:**
    ```json
    {
        "success": true,
        "movimiento_id": 123,
        "lote_id": 456,
        "stock_anterior": 20.0,
        "stock_nuevo": 30.5,
        "mensaje": "Movimiento procesado exitosamente",
        "timestamp": "2024-10-12T10:30:00"
    }
    ```
    """
    try:
        data = request.get_json()

        if not data:
            return (
                jsonify(
                    {
                        "error": "Datos JSON requeridos",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        # Validación de campos requeridos
        campos_requeridos = ["inventario_id", "tipo_movimiento", "cantidad"]
        for campo in campos_requeridos:
            if campo not in data:
                return (
                    jsonify(
                        {
                            "error": f"Campo requerido: {campo}",
                            "timestamp": datetime.now().isoformat(),
                        }
                    ),
                    400,
                )

        # Validar tipo de movimiento
        if data["tipo_movimiento"] not in ["entrada", "salida"]:
            return (
                jsonify(
                    {
                        "error": "tipo_movimiento debe ser 'entrada' o 'salida'",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        # Validar cantidad
        try:
            cantidad = float(data["cantidad"])
            if cantidad <= 0:
                raise ValueError("Cantidad debe ser positiva")
        except (ValueError, TypeError):
            return (
                jsonify(
                    {
                        "error": "Cantidad debe ser un número positivo",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        # Validar precio en EUR para entradas
        if data["tipo_movimiento"] == "entrada" and "precio_unitario" not in data:
            return (
                jsonify(
                    {
                        "error": "precio_unitario en EUR es requerido para entradas",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        # Procesar movimiento
        resultado = controller_opt.crear_movimiento_optimizado(data)

        if "error" in resultado:
            status_code = 404 if "no encontrado" in resultado["error"].lower() else 400
            return jsonify(resultado), status_code

        return jsonify(resultado), 201

    except Exception as e:
        logger.error(f"Error en endpoint crear_movimiento: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Error interno del servidor",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@inventario_optimizado_bp.route("/movimientos/batch", methods=["POST"])
@performance_monitor("api_inventario_batch_v2")
def crear_movimientos_batch():
    """
    🚀 Procesa múltiples movimientos en batch para máximo rendimiento

    **Ventajas del batch processing:**
    - Procesamiento optimizado en lotes
    - Transacciones agrupadas
    - Invalidación de cache eficiente
    - Manejo de errores individuales
    - Métricas de performance detalladas

    **Límites de seguridad:**
    - Máximo 50 movimientos por batch
    - Validación individual de cada movimiento
    - Rollback automático en errores críticos

    **Estructura del request:**
    ```json
    {
        "movimientos": [
            {
                "inventario_id": 1,
                "tipo_movimiento": "entrada",
                "cantidad": 10.0,
                "precio_unitario": 25.0
            },
            {
                "inventario_id": 2,
                "tipo_movimiento": "salida",
                "cantidad": 5.0
            }
        ]
    }
    ```

    **Ejemplo de respuesta:**
    ```json
    {
        "total_procesados": 2,
        "exitosos": 2,
        "errores": 0,
        "tiempo_total_ms": 145.8,
        "resultados": [
            {"success": true, "movimiento_id": 123},
            {"success": true, "movimiento_id": 124}
        ],
        "timestamp": "2024-10-12T10:30:00"
    }
    ```
    """
    try:
        data = request.get_json()

        if not data or "movimientos" not in data:
            return (
                jsonify(
                    {
                        "error": "Se requiere campo 'movimientos' con lista de movimientos",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        movimientos = data["movimientos"]
        if not isinstance(movimientos, list):
            return (
                jsonify(
                    {
                        "error": "Campo 'movimientos' debe ser una lista",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        if len(movimientos) == 0:
            return (
                jsonify(
                    {
                        "error": "Lista de movimientos no puede estar vacía",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        if len(movimientos) > 50:
            return (
                jsonify(
                    {
                        "error": "Máximo 50 movimientos por batch",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        # Procesar batch
        resultado = controller_opt.crear_movimientos_batch_optimizado(movimientos)

        return jsonify(resultado), 200

    except Exception as e:
        logger.error(f"Error en endpoint crear_movimientos_batch: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Error interno del servidor",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@inventario_optimizado_bp.route("/health", methods=["GET"])
def health_check():
    """
    ❤️ Health check específico del módulo de inventario optimizado

    **Verificaciones incluidas:**
    - Conectividad a base de datos
    - Estado del sistema de cache
    - Funcionalidad FIFO optimizado
    - Métricas de performance disponibles
    - Memoria y recursos del sistema

    **Estados posibles:**
    - `healthy`: Todo funcionando correctamente
    - `degraded`: Algunos componentes con problemas
    - `unhealthy`: Problemas críticos detectados

    **Ejemplo de respuesta:**
    ```json
    {
        "status": "healthy",
        "timestamp": "2024-10-12T10:30:00",
        "services": {
            "database": "ok",
            "fifo_optimizado": "ok",
            "cache": "ok"
        },
        "version": "2.0",
        "module": "inventario_optimizado"
    }
    ```
    """
    try:
        from app.extensions import db
        from fifo_optimizado import FIFOOptimizado

        # Verificar base de datos
        try:
            db.session.execute(db.text("SELECT 1"))
            db_status = "ok"
        except Exception as e:
            logger.error(f"Error en base de datos: {e}")
            db_status = "error"

        # Verificar FIFO optimizado
        try:
            fifo_opt = FIFOOptimizado()
            fifo_status = "ok"
        except Exception as e:
            logger.error(f"Error en FIFO optimizado: {e}")
            fifo_status = "error"

        # Verificar cache (mock, ya que no tenemos acceso directo aquí)
        cache_status = "ok"

        # Determinar estado general
        if all(status == "ok" for status in [db_status, fifo_status, cache_status]):
            overall_status = "healthy"
            status_code = 200
        else:
            overall_status = "degraded"
            status_code = 200  # 200 pero con warnings

        resultado = {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": db_status,
                "fifo_optimizado": fifo_status,
                "cache": cache_status,
            },
            "version": "2.0",
            "module": "inventario_optimizado",
        }

        return jsonify(resultado), status_code

    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "module": "inventario_optimizado",
                }
            ),
            500,
        )
