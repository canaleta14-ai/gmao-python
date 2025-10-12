#!/usr/bin/env python3
"""
🚀 BLUEPRINT DE INVENTARIO OPTIMIZADO
Endpoints con todas las optimizaciones integradas
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
    """Listar inventario con optimizaciones completas"""
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
    """Estadísticas de inventario optimizadas"""
    try:
        resultado = controller_opt.obtener_estadisticas_optimizado()

        if "error" in resultado:
            return jsonify(resultado), 500

        # Mejorar la estructura de respuesta para facilitar el uso
        if "estadisticas" in resultado:
            # Combinar las estadísticas con los metadatos
            respuesta = resultado["estadisticas"].copy()
            respuesta.update(
                {
                    "from_cache": resultado.get("from_cache", False),
                    "timestamp": resultado.get("timestamp"),
                    "cached": resultado.get(
                        "from_cache", False
                    ),  # Alias para compatibilidad
                    "response_time_ms": resultado.get(
                        "response_time_ms"
                    ),  # Agregado por performance_monitor
                }
            )
            return jsonify(respuesta), 200
        else:
            return jsonify(resultado), 200

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
    """Obtener artículo específico optimizado"""
    try:
        resultado = controller_opt.obtener_articulo_optimizado(inventario_id)

        if "error" in resultado and "no encontrado" in resultado["error"]:
            return jsonify(resultado), 404
        elif "error" in resultado:
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


@inventario_optimizado_bp.route("/movimientos", methods=["POST"])
@performance_monitor("api_inventario_movimiento_v2")
def crear_movimiento():
    """Crear movimiento con FIFO optimizado"""
    try:
        data = request.get_json()

        if not data:
            return (
                jsonify(
                    {
                        "error": "Datos requeridos",
                        "message": "El cuerpo de la petición debe contener datos JSON",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        # Validar campos requeridos
        required_fields = ["inventario_id", "cantidad", "tipo_movimiento"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return (
                jsonify(
                    {
                        "error": "Campos requeridos faltantes",
                        "missing_fields": missing_fields,
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        resultado = controller_opt.crear_movimiento_optimizado(data)

        if resultado.get("status") == "error":
            return jsonify(resultado), 400

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


@inventario_optimizado_bp.route("/<int:inventario_id>/lotes", methods=["GET"])
@performance_monitor("api_inventario_lotes_v2")
def obtener_lotes_articulo(inventario_id):
    """Obtener lotes de un artículo usando FIFO optimizado"""
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


@inventario_optimizado_bp.route("/movimientos/batch", methods=["POST"])
@performance_monitor("api_inventario_batch_v2")
def crear_movimientos_batch():
    """Crear múltiples movimientos en lote con FIFO optimizado"""
    try:
        data = request.get_json()

        if not data or "movimientos" not in data:
            return (
                jsonify(
                    {
                        "error": "Datos requeridos",
                        "message": "Se requiere un array 'movimientos' en el cuerpo JSON",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        movimientos = data["movimientos"]

        if not movimientos:
            return (
                jsonify(
                    {
                        "error": "Lista vacía",
                        "message": "El array 'movimientos' no puede estar vacío",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        # Procesar movimientos
        resultados = []
        errores = []

        for i, mov_data in enumerate(movimientos):
            try:
                resultado = controller_opt.crear_movimiento_optimizado(mov_data)

                if resultado.get("status") == "error":
                    errores.append(
                        {
                            "indice": i,
                            "movimiento": mov_data,
                            "error": resultado.get("message", "Error desconocido"),
                        }
                    )
                else:
                    resultados.append({"indice": i, "resultado": resultado})

            except Exception as e:
                errores.append({"indice": i, "movimiento": mov_data, "error": str(e)})

        # Respuesta consolidada
        response = {
            "status": "completed",
            "total_procesados": len(movimientos),
            "exitosos": len(resultados),
            "fallidos": len(errores),
            "resultados": resultados,
            "timestamp": datetime.now().isoformat(),
        }

        if errores:
            response["errores"] = errores
            response["status"] = "parcial" if len(resultados) > 0 else "failed"

        status_code = 200 if len(errores) == 0 else 207  # 207 Multi-Status
        return jsonify(response), status_code

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
@performance_monitor("api_inventario_health_v2")
def health_check():
    """Health check del sistema optimizado"""
    try:
        from app.extensions import db
        from fifo_optimizado import FIFOOptimizado
        from sqlalchemy import text

        # Verificar base de datos
        db.session.execute(text("SELECT 1"))

        # Verificar FIFO optimizado
        fifo_opt = FIFOOptimizado()
        stats = fifo_opt._stats.copy()

        # Verificar caché
        from app.blueprints.cached_inventario_simple import _cache

        cache_size = len(_cache)

        return (
            jsonify(
                {
                    "status": "healthy",
                    "services": {
                        "database": "ok",
                        "fifo_optimizado": "ok",
                        "cache": "ok",
                    },
                    "metrics": {"fifo_stats": stats, "cache_size": cache_size},
                    "version": "v2-optimized",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            503,
        )


@inventario_optimizado_bp.route("/cache/clear", methods=["POST"])
@performance_monitor("api_inventario_cache_clear_v2")
def limpiar_cache_inventario():
    """Limpiar caché del inventario"""
    try:
        from app.blueprints.cached_inventario_simple import _cache, _cache_ttl

        cache_size_antes = len(_cache)

        # Limpiar cachés relacionados con inventario
        keys_to_remove = []
        for key in _cache.keys():
            if any(
                pattern in key for pattern in ["inventario", "estadisticas", "articulo"]
            ):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            _cache.pop(key, None)
            _cache_ttl.pop(key, None)

        cache_size_despues = len(_cache)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Cache limpiado: {len(keys_to_remove)} entradas eliminadas",
                    "cache_antes": cache_size_antes,
                    "cache_despues": cache_size_despues,
                    "entradas_eliminadas": len(keys_to_remove),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error limpiando cache: {str(e)}")
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
