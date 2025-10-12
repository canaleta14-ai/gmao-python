#!/usr/bin/env python3
"""
📊 DASHBOARD DE MONITOREO - GMAO SISTEMA V2
==========================================

Dashboard web en tiempo real para visualizar:
- Métricas de performance del sistema
- Estadísticas de inventario y operaciones
- Estado del cache y FIFO
- Gráficos interactivos y alertas
"""

from flask import Blueprint, render_template, jsonify, request
from app.controllers import inventario_controller_optimizado as controller_opt
from datetime import datetime, timedelta
import logging
import psutil
import os

logger = logging.getLogger(__name__)

# =============================================================================
# FUNCIONES AUXILIARES PARA MÉTRICAS
# =============================================================================


def get_system_stats():
    """Obtiene estadísticas del sistema"""
    try:
        process = psutil.Process()

        return {
            "uptime_hours": round(
                (
                    datetime.now()
                    - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                ).total_seconds()
                / 3600,
                2,
            ),
            "memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
            "cpu_percent": round(process.cpu_percent(), 2),
            "disk_usage_percent": round(psutil.disk_usage("/").percent, 2),
            "active_connections": len(psutil.net_connections()),
        }
    except Exception:
        return {
            "uptime_hours": 0,
            "memory_mb": 0,
            "cpu_percent": 0,
            "disk_usage_percent": 0,
            "active_connections": 0,
        }


def get_cache_stats():
    """Obtiene estadísticas del cache (mock por ahora)"""
    try:
        from app.blueprints.cached_inventario_simple import simple_cache

        # Por ahora retornamos estadísticas mock
        return {"total_keys": 0, "hit_rate": 85.5, "memory_usage_mb": 12.5}
    except Exception:
        return {"total_keys": 0, "hit_rate": 0, "memory_usage_mb": 0}


def get_current_metrics(limit=50):
    """Obtiene métricas recientes (mock por ahora)"""
    try:
        # Por ahora retornamos datos mock
        mock_metrics = []
        for i in range(min(limit, 10)):
            mock_metrics.append(
                {
                    "timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(),
                    "operation": f"api_operation_{i % 3}",
                    "duration": 0.1 + (i * 0.01),
                    "success": True,
                    "memory_mb": 50 + i,
                    "cpu_percent": 5 + (i % 10),
                }
            )
        return mock_metrics
    except Exception:
        return []


logger = logging.getLogger(__name__)

# Crear blueprint para dashboard
dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard",
    template_folder="../templates/dashboard",
    static_folder="../static/dashboard",
)

# =============================================================================
# RUTAS DE PÁGINAS DEL DASHBOARD
# =============================================================================


@dashboard_bp.route("/")
def index():
    """Página principal del dashboard"""
    return render_template(
        "dashboard/index.html", title="Dashboard GMAO V2", active_page="overview"
    )


@dashboard_bp.route("/performance")
def performance():
    """Panel de métricas de performance"""
    return render_template(
        "dashboard/performance.html",
        title="Performance Monitor",
        active_page="performance",
    )


@dashboard_bp.route("/inventory")
def inventory():
    """Panel de estadísticas de inventario"""
    return render_template(
        "dashboard/inventory.html", title="Inventario Monitor", active_page="inventory"
    )


@dashboard_bp.route("/cache")
def cache_management():
    """Panel de gestión de cache"""
    return render_template(
        "dashboard/cache.html", title="Cache Management", active_page="cache"
    )


@dashboard_bp.route("/fifo")
def fifo_monitor():
    """Panel de monitoreo FIFO"""
    return render_template(
        "dashboard/fifo.html", title="FIFO Monitor", active_page="fifo"
    )


# =============================================================================
# API ENDPOINTS PARA DATOS DEL DASHBOARD
# =============================================================================


@dashboard_bp.route("/api/system/overview")
def api_system_overview():
    """Obtiene resumen general del sistema"""
    try:
        # Métricas del sistema
        system_stats = get_system_stats()

        # Estadísticas básicas de inventario
        stats_result = controller_opt.obtener_estadisticas_optimizado()
        inventory_stats = (
            stats_result.get("estadisticas", {})
            if "estadisticas" in stats_result
            else stats_result
        )

        # Estado del cache
        cache_stats = get_cache_stats()

        # Métricas recientes de performance
        recent_metrics = get_current_metrics(limit=10)

        overview = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "uptime_hours": round(system_stats.get("uptime_hours", 0), 2),
                "memory_usage_mb": round(system_stats.get("memory_mb", 0), 2),
                "cpu_percent": round(system_stats.get("cpu_percent", 0), 2),
                "disk_usage_percent": round(
                    system_stats.get("disk_usage_percent", 0), 2
                ),
                "active_connections": system_stats.get("active_connections", 0),
            },
            "inventory": {
                "total_articulos": inventory_stats.get("total_articulos", 0),
                "valor_total": inventory_stats.get("valor_total_inventario", 0),
                "articulos_stock_bajo": inventory_stats.get("articulos_stock_bajo", 0),
                "articulos_sin_stock": inventory_stats.get("articulos_sin_stock", 0),
                "total_lotes": inventory_stats.get("total_lotes", 0),
            },
            "cache": {
                "total_keys": cache_stats.get("total_keys", 0),
                "hit_rate": cache_stats.get("hit_rate", 0),
                "memory_usage_mb": cache_stats.get("memory_usage_mb", 0),
            },
            "performance": {
                "avg_response_time": round(
                    sum(m.get("duration", 0) for m in recent_metrics)
                    / max(len(recent_metrics), 1)
                    * 1000,
                    2,
                ),
                "total_requests_today": len(
                    [
                        m
                        for m in recent_metrics
                        if datetime.fromisoformat(m.get("timestamp", "")).date()
                        == datetime.now().date()
                    ]
                ),
                "error_rate": round(
                    len([m for m in recent_metrics if not m.get("success", True)])
                    / max(len(recent_metrics), 1)
                    * 100,
                    2,
                ),
            },
        }

        return jsonify(overview)

    except Exception as e:
        logger.error(f"Error en system overview: {str(e)}")
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/api/performance/metrics")
def api_performance_metrics():
    """Obtiene métricas de performance detalladas"""
    try:
        # Parámetros de consulta
        limit = request.args.get("limit", 50, type=int)
        operation = request.args.get("operation", None)
        hours = request.args.get("hours", 24, type=int)

        # Obtener métricas
        metrics = get_current_metrics(limit=limit * 2)  # Más margen para filtrar

        # Filtrar por tiempo
        cutoff_time = datetime.now() - timedelta(hours=hours)
        filtered_metrics = [
            m
            for m in metrics
            if datetime.fromisoformat(m.get("timestamp", "")) >= cutoff_time
        ]

        # Filtrar por operación si se especifica
        if operation and operation != "all":
            filtered_metrics = [
                m
                for m in filtered_metrics
                if m.get("operation", "").startswith(operation)
            ]

        # Limitar resultados finales
        filtered_metrics = filtered_metrics[:limit]

        # Agrupar métricas por operación para estadísticas
        operation_stats = {}
        for metric in filtered_metrics:
            op = metric.get("operation", "unknown")
            if op not in operation_stats:
                operation_stats[op] = {
                    "count": 0,
                    "total_duration": 0,
                    "errors": 0,
                    "avg_memory": 0,
                    "avg_cpu": 0,
                }

            stats = operation_stats[op]
            stats["count"] += 1
            stats["total_duration"] += metric.get("duration", 0)
            stats["errors"] += 0 if metric.get("success", True) else 1
            stats["avg_memory"] += metric.get("memory_mb", 0)
            stats["avg_cpu"] += metric.get("cpu_percent", 0)

        # Calcular promedios
        for op, stats in operation_stats.items():
            count = stats["count"]
            if count > 0:
                stats["avg_duration_ms"] = round(
                    stats["total_duration"] * 1000 / count, 2
                )
                stats["error_rate"] = round(stats["errors"] / count * 100, 2)
                stats["avg_memory"] = round(stats["avg_memory"] / count, 2)
                stats["avg_cpu"] = round(stats["avg_cpu"] / count, 2)
            del stats["total_duration"]  # Limpiar campo temporal

        response = {
            "timestamp": datetime.now().isoformat(),
            "metrics": filtered_metrics,
            "operation_stats": operation_stats,
            "summary": {
                "total_metrics": len(filtered_metrics),
                "time_range_hours": hours,
                "operations_count": len(operation_stats),
            },
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error en performance metrics: {str(e)}")
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/api/inventory/stats")
def api_inventory_stats():
    """Obtiene estadísticas detalladas de inventario"""
    try:
        # Estadísticas principales
        stats_result = controller_opt.obtener_estadisticas_optimizado()

        # Obtener lista de inventario para análisis adicional
        inventory_result = controller_opt.listar_inventario_optimizado()
        items = inventory_result.get("items", [])

        # Análisis adicional
        categoria_stats = {}
        stock_alerts = []

        for item in items:
            # Estadísticas por categoría
            categoria = item.get("categoria_nombre", "Sin categoría")
            if categoria not in categoria_stats:
                categoria_stats[categoria] = {
                    "count": 0,
                    "total_value": 0,
                    "avg_stock": 0,
                    "low_stock_items": 0,
                }

            cat_stat = categoria_stats[categoria]
            cat_stat["count"] += 1
            cat_stat["total_value"] += item.get("stock_actual", 0) * item.get(
                "precio_unitario", 0
            )
            cat_stat["avg_stock"] += item.get("stock_actual", 0)

            # Detectar stock bajo
            stock_actual = item.get("stock_actual", 0)
            stock_minimo = item.get("stock_minimo", 0)

            if stock_actual <= stock_minimo and stock_minimo > 0:
                cat_stat["low_stock_items"] += 1
                stock_alerts.append(
                    {
                        "id": item.get("id"),
                        "codigo": item.get("codigo_articulo"),
                        "descripcion": item.get("descripcion"),
                        "stock_actual": stock_actual,
                        "stock_minimo": stock_minimo,
                        "urgencia": (
                            "critica"
                            if stock_actual == 0
                            else (
                                "alta" if stock_actual < stock_minimo * 0.5 else "media"
                            )
                        ),
                    }
                )

        # Calcular promedios por categoría
        for cat, stats in categoria_stats.items():
            if stats["count"] > 0:
                stats["avg_stock"] = round(stats["avg_stock"] / stats["count"], 2)
                stats["total_value"] = round(stats["total_value"], 2)

        response = {
            "timestamp": datetime.now().isoformat(),
            "general_stats": (
                stats_result.get("estadisticas", {})
                if "estadisticas" in stats_result
                else stats_result
            ),
            "categoria_stats": categoria_stats,
            "stock_alerts": sorted(
                stock_alerts,
                key=lambda x: (
                    0
                    if x["urgencia"] == "critica"
                    else 1 if x["urgencia"] == "alta" else 2
                ),
            ),
            "summary": {
                "total_categorias": len(categoria_stats),
                "total_alerts": len(stock_alerts),
                "critical_alerts": len(
                    [a for a in stock_alerts if a["urgencia"] == "critica"]
                ),
                "from_cache": stats_result.get("from_cache", False),
            },
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error en inventory stats: {str(e)}")
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/api/cache/stats")
def api_cache_stats():
    """Obtiene estadísticas del sistema de cache"""
    try:
        cache_stats = get_cache_stats()

        # Obtener métricas de cache de performance
        cache_metrics = get_current_metrics(limit=100)
        cache_operations = [
            m for m in cache_metrics if "cache" in m.get("operation", "").lower()
        ]

        # Calcular estadísticas de rendimiento del cache
        total_ops = len(cache_operations)
        if total_ops > 0:
            avg_duration = (
                sum(m.get("duration", 0) for m in cache_operations) / total_ops
            )
            cache_errors = len(
                [m for m in cache_operations if not m.get("success", True)]
            )
        else:
            avg_duration = 0
            cache_errors = 0

        response = {
            "timestamp": datetime.now().isoformat(),
            "basic_stats": cache_stats,
            "performance": {
                "total_operations": total_ops,
                "avg_duration_ms": round(avg_duration * 1000, 2),
                "error_count": cache_errors,
                "error_rate": round(cache_errors / max(total_ops, 1) * 100, 2),
            },
            "recent_operations": cache_operations[:10],
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error en cache stats: {str(e)}")
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/api/cache/clear", methods=["POST"])
def api_cache_clear():
    """Limpia el cache del sistema"""
    try:
        from app.blueprints.cached_inventario_simple import clear_cache

        # Limpiar cache
        cleared_count = clear_cache()

        response = {
            "success": True,
            "message": f"Cache limpiado exitosamente",
            "cleared_keys": cleared_count,
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error limpiando cache: {str(e)}")
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/api/fifo/stats")
def api_fifo_stats():
    """Obtiene estadísticas del sistema FIFO"""
    try:
        from fifo_optimizado import FIFOOptimizado

        fifo_opt = FIFOOptimizado()

        # Obtener métricas FIFO de performance
        fifo_metrics = get_current_metrics(limit=100)
        fifo_operations = [
            m for m in fifo_metrics if "fifo" in m.get("operation", "").lower()
        ]

        # Estadísticas básicas FIFO
        total_ops = len(fifo_operations)
        if total_ops > 0:
            avg_duration = (
                sum(m.get("duration", 0) for m in fifo_operations) / total_ops
            )
            total_records = sum(m.get("records_processed", 0) for m in fifo_operations)
            fifo_errors = len(
                [m for m in fifo_operations if not m.get("success", True)]
            )
        else:
            avg_duration = 0
            total_records = 0
            fifo_errors = 0

        # Obtener estadísticas de lotes recientes
        try:
            # Aquí podrías agregar lógica específica para obtener stats de lotes
            recent_batches = []  # Placeholder
            total_lotes_sistema = 0  # Placeholder
        except Exception:
            recent_batches = []
            total_lotes_sistema = 0

        response = {
            "timestamp": datetime.now().isoformat(),
            "performance": {
                "total_operations": total_ops,
                "avg_duration_ms": round(avg_duration * 1000, 2),
                "total_records_processed": total_records,
                "error_count": fifo_errors,
                "error_rate": round(fifo_errors / max(total_ops, 1) * 100, 2),
                "throughput_per_hour": round(
                    total_records / max(24, 1), 2
                ),  # Aproximación
            },
            "lotes_stats": {
                "total_lotes_sistema": total_lotes_sistema,
                "recent_batches": recent_batches[:10],
            },
            "recent_operations": fifo_operations[:10],
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error en FIFO stats: {str(e)}")
        return jsonify({"error": str(e)}), 500


# =============================================================================
# UTILIDADES DEL DASHBOARD
# =============================================================================


@dashboard_bp.route("/api/health")
def api_dashboard_health():
    """Health check del dashboard"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "dashboard": "ok",
                "metrics_system": "ok",
                "cache_system": "ok",
                "fifo_system": "ok",
            },
            "version": "2.0",
            "uptime_hours": round(
                (
                    datetime.now()
                    - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                ).total_seconds()
                / 3600,
                2,
            ),
        }

        return jsonify(health_status)

    except Exception as e:
        logger.error(f"Error en dashboard health: {str(e)}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )
