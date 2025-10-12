#!/usr/bin/env python3
"""
🚀 BLUEPRINT DE MÉTRICAS DE PERFORMANCE
Sistema de monitoreo en tiempo real
"""

from flask import Blueprint, jsonify, request
import time
import psutil
import threading
from datetime import datetime, timedelta
from collections import deque, defaultdict
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from functools import wraps
import json

# Sistema de métricas global
_metrics = deque(maxlen=1000)
_operation_stats = defaultdict(list)
_throughput_counters = defaultdict(int)
_start_time = datetime.now()
_process = psutil.Process()
_lock = threading.Lock()


@dataclass
class PerformanceMetric:
    """Métrica individual de performance"""

    timestamp: str
    operation: str
    duration: float
    memory_mb: float
    cpu_percent: float
    records_processed: int
    success: bool
    error_message: Optional[str] = None


def record_metric(
    operation: str,
    duration: float,
    records: int = 0,
    success: bool = True,
    error: str = None,
):
    """Registra una métrica de performance"""
    try:
        memory_mb = _process.memory_info().rss / 1024 / 1024
        cpu_percent = _process.cpu_percent()

        metric = PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            operation=operation,
            duration=duration,
            memory_mb=memory_mb,
            cpu_percent=cpu_percent,
            records_processed=records,
            success=success,
            error_message=error,
        )

        with _lock:
            _metrics.append(metric)
            _operation_stats[operation].append(metric)
            _throughput_counters[operation] += 1

    except Exception as e:
        print(f"Error recording metric: {e}")


def performance_monitor(operation_name: str):
    """Decorador para monitorear performance de funciones"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None
            records = 0

            try:
                result = func(*args, **kwargs)

                # Intentar determinar número de registros procesados
                if isinstance(result, dict):
                    if "items" in result and isinstance(result["items"], list):
                        records = len(result["items"])
                    elif "lotes_fifo" in result and isinstance(
                        result["lotes_fifo"], list
                    ):
                        records = len(result["lotes_fifo"])
                    elif "total_inventarios" in result:
                        records = result.get("total_inventarios", 0)
                elif isinstance(result, list):
                    records = len(result)

                return result

            except Exception as e:
                success = False
                error = str(e)
                raise
            finally:
                duration = time.time() - start_time
                record_metric(operation_name, duration, records, success, error)

        return wrapper

    return decorator


# Crear blueprint para métricas de performance
performance_bp = Blueprint("performance", __name__, url_prefix="/api/performance")


@performance_bp.route("/metrics")
def get_performance_metrics():
    """Obtener todas las métricas de performance"""
    with _lock:
        # Convertir las últimas 50 métricas
        recent_metrics = list(_metrics)[-50:]
        metrics_data = [asdict(metric) for metric in recent_metrics]

    return jsonify(
        {
            "total_metrics": len(_metrics),
            "recent_metrics": metrics_data,
            "uptime_seconds": (datetime.now() - _start_time).total_seconds(),
        }
    )


@performance_bp.route("/stats")
def get_performance_stats():
    """Obtener estadísticas resumidas de performance"""
    with _lock:
        stats = {}

        for operation, metrics in _operation_stats.items():
            if not metrics:
                continue

            durations = [m.duration for m in metrics]
            memories = [m.memory_mb for m in metrics]
            successes = [m.success for m in metrics]

            stats[operation] = {
                "count": len(metrics),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "avg_memory": sum(memories) / len(memories),
                "success_rate": (sum(successes) / len(successes)) * 100,
                "total_records": sum(m.records_processed for m in metrics),
                "throughput": _throughput_counters[operation],
            }

    # Estadísticas del sistema
    try:
        system_stats = {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_mb": psutil.virtual_memory().available / 1024 / 1024,
            "disk_usage_percent": psutil.disk_usage("/").percent,
        }
    except:
        system_stats = {"error": "Could not get system stats"}

    return jsonify(
        {
            "operation_stats": stats,
            "system_stats": system_stats,
            "uptime_seconds": (datetime.now() - _start_time).total_seconds(),
        }
    )


@performance_bp.route("/operation/<operation_name>")
def get_operation_stats(operation_name):
    """Obtener estadísticas de una operación específica"""
    with _lock:
        if operation_name not in _operation_stats:
            return jsonify({"error": "Operation not found"}), 404

        metrics = _operation_stats[operation_name]
        recent_metrics = metrics[-20:]  # Últimas 20 métricas

        durations = [m.duration for m in metrics]

        return jsonify(
            {
                "operation": operation_name,
                "total_executions": len(metrics),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "recent_metrics": [asdict(m) for m in recent_metrics],
                "throughput": _throughput_counters[operation_name],
            }
        )


@performance_bp.route("/dashboard")
def get_performance_dashboard():
    """Dashboard completo de performance"""
    with _lock:
        # Top operaciones por duración
        top_operations = []
        for operation, metrics in _operation_stats.items():
            if metrics:
                avg_duration = sum(m.duration for m in metrics) / len(metrics)
                top_operations.append(
                    {
                        "operation": operation,
                        "avg_duration": avg_duration,
                        "count": len(metrics),
                        "success_rate": (sum(m.success for m in metrics) / len(metrics))
                        * 100,
                    }
                )

        top_operations.sort(key=lambda x: x["avg_duration"], reverse=True)

        # Métricas por hora (últimas 24 horas)
        now = datetime.now()
        hourly_stats = defaultdict(lambda: {"count": 0, "avg_duration": 0, "errors": 0})

        for metric in _metrics:
            metric_time = datetime.fromisoformat(metric.timestamp)
            if now - metric_time <= timedelta(hours=24):
                hour_key = metric_time.strftime("%Y-%m-%d %H:00")
                hourly_stats[hour_key]["count"] += 1
                hourly_stats[hour_key]["avg_duration"] += metric.duration
                if not metric.success:
                    hourly_stats[hour_key]["errors"] += 1

        # Calcular promedios
        for hour_data in hourly_stats.values():
            if hour_data["count"] > 0:
                hour_data["avg_duration"] /= hour_data["count"]

    return jsonify(
        {
            "top_slowest_operations": top_operations[:10],
            "hourly_stats": dict(hourly_stats),
            "total_operations": len(_metrics),
            "active_operations": len(_operation_stats),
        }
    )


@performance_bp.route("/clear", methods=["POST"])
def clear_metrics():
    """Limpiar todas las métricas"""
    with _lock:
        _metrics.clear()
        _operation_stats.clear()
        _throughput_counters.clear()

    return jsonify({"message": "Performance metrics cleared"})


@performance_bp.route("/test")
def test_performance_monitoring():
    """Endpoint de prueba para generar métricas"""

    @performance_monitor("test_operation")
    def test_function():
        time.sleep(0.1)  # Simular trabajo
        return {"items": list(range(10)), "processed": True}

    result = test_function()

    return jsonify(
        {
            "message": "Test operation completed",
            "result": result,
            "metrics_count": len(_metrics),
        }
    )


# Funciones utilitarias para integrar en otros módulos
def monitor_inventory_operation(operation_name: str):
    """Wrapper específico para operaciones de inventario"""
    return performance_monitor(f"inventory_{operation_name}")


def monitor_fifo_operation(operation_name: str):
    """Wrapper específico para operaciones FIFO"""
    return performance_monitor(f"fifo_{operation_name}")


def monitor_database_operation(operation_name: str):
    """Wrapper específico para operaciones de base de datos"""
    return performance_monitor(f"db_{operation_name}")


# Obtener estadísticas actuales (para uso programático)
def get_current_stats():
    """Obtener estadísticas actuales de performance"""
    with _lock:
        return {
            "total_metrics": len(_metrics),
            "active_operations": len(_operation_stats),
            "uptime": (datetime.now() - _start_time).total_seconds(),
        }
