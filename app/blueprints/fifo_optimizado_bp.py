#!/usr/bin/env python3
"""
🚀 BLUEPRINT DE FIFO OPTIMIZADO
Integración del sistema FIFO optimizado para endpoints de alta performance
"""

from flask import Blueprint, jsonify, request
from app.models.inventario import Inventario
from app.models.lote_inventario import LoteInventario
from app.extensions import db
from app.blueprints.performance_metrics import performance_monitor
from datetime import datetime
import time
from typing import List, Dict, Any

# Importar el sistema FIFO optimizado
from fifo_optimizado import FIFOOptimizado

# Crear instancia global del servicio optimizado
fifo_optimizado = FIFOOptimizado()

# Crear blueprint para endpoints optimizados
fifo_optimizado_bp = Blueprint("fifo_optimizado", __name__, url_prefix="/api/fifo")


@fifo_optimizado_bp.route("/test")
@performance_monitor("fifo_test_operation")
def test_fifo_optimizado():
    """Endpoint de prueba para verificar que el FIFO optimizado funciona"""
    try:
        # Crear algunas operaciones de test si no existen datos
        inventario_test = Inventario.query.first()

        if not inventario_test:
            return jsonify(
                {
                    "status": "warning",
                    "message": "No hay datos de inventario para probar",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # Test básico del sistema
        stats = fifo_optimizado._stats.copy()

        return jsonify(
            {
                "status": "success",
                "message": "FIFO optimizado funcionando correctamente",
                "fifo_stats": stats,
                "inventario_disponible": inventario_test.nombre,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Error en test FIFO optimizado: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@fifo_optimizado_bp.route("/consumo/batch", methods=["POST"])
@performance_monitor("fifo_consumo_batch")
def consumo_fifo_batch():
    """
    Endpoint para consumo FIFO en lote optimizado

    Body esperado:
    {
        "operaciones": [
            {
                "inventario_id": 1,
                "cantidad": 10.0,
                "orden_trabajo_id": 123,
                "documento_referencia": "OT-001",
                "observaciones": "Consumo automático"
            }
        ],
        "usuario_id": "user123"
    }
    """
    try:
        data = request.get_json()

        if not data or "operaciones" not in data:
            return (
                jsonify({"error": "Formato inválido. Se requiere 'operaciones'"}),
                400,
            )

        operaciones = data["operaciones"]
        usuario_id = data.get("usuario_id")

        if not operaciones:
            return jsonify({"error": "Lista de operaciones vacía"}), 400

        # Validar operaciones
        for i, op in enumerate(operaciones):
            if "inventario_id" not in op or "cantidad" not in op:
                return (
                    jsonify(
                        {
                            "error": f"Operación {i}: faltan campos requeridos (inventario_id, cantidad)"
                        }
                    ),
                    400,
                )

        # Procesar con FIFO optimizado
        start_time = time.time()
        resultados = fifo_optimizado.consumir_fifo_batch(operaciones, usuario_id)
        processing_time = time.time() - start_time

        # Formatear resultados para respuesta
        respuesta_resultados = []
        total_operaciones = 0
        total_cantidad_procesada = 0.0

        for resultado in resultados:
            total_operaciones += resultado.operaciones_realizadas
            total_cantidad_procesada += resultado.cantidad_procesada

            respuesta_resultados.append(
                {
                    "lotes_afectados": len(resultado.lotes_afectados),
                    "cantidad_procesada": float(resultado.cantidad_procesada),
                    "cantidad_faltante": float(resultado.cantidad_faltante),
                    "tiempo_ejecucion": resultado.tiempo_ejecucion,
                    "operaciones_realizadas": resultado.operaciones_realizadas,
                }
            )

        return jsonify(
            {
                "status": "success",
                "message": f"Batch FIFO completado: {len(operaciones)} operaciones",
                "processing_time": processing_time,
                "summary": {
                    "total_operaciones": len(operaciones),
                    "total_cantidad_procesada": total_cantidad_procesada,
                    "total_db_operations": total_operaciones,
                },
                "resultados": respuesta_resultados,
                "fifo_stats": fifo_optimizado._stats.copy(),
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Error en consumo batch: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@fifo_optimizado_bp.route("/inventario/<int:inventario_id>/lotes/disponibles")
@performance_monitor("fifo_lotes_disponibles")
def obtener_lotes_disponibles(inventario_id):
    """Obtener lotes disponibles con cache optimizado"""
    try:
        lotes = fifo_optimizado._obtener_lotes_optimizado(inventario_id)

        lotes_info = []
        total_disponible = 0.0

        for lote in lotes:
            if lote.cantidad_disponible > 0:
                lote_info = {
                    "id": lote.id,
                    "codigo": lote.codigo,
                    "cantidad_disponible": float(lote.cantidad_disponible),
                    "fecha_entrada": (
                        lote.fecha_entrada.isoformat() if lote.fecha_entrada else None
                    ),
                    "fecha_vencimiento": (
                        lote.fecha_vencimiento.isoformat()
                        if lote.fecha_vencimiento
                        else None
                    ),
                    "proveedor": lote.proveedor,
                    "documento_referencia": lote.documento_referencia,
                }
                lotes_info.append(lote_info)
                total_disponible += lote.cantidad_disponible

        return jsonify(
            {
                "status": "success",
                "inventario_id": inventario_id,
                "total_lotes": len(lotes_info),
                "total_disponible": total_disponible,
                "lotes": lotes_info,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Error obteniendo lotes: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@fifo_optimizado_bp.route("/stats")
@performance_monitor("fifo_stats")
def obtener_estadisticas_fifo():
    """Obtener estadísticas del sistema FIFO optimizado"""
    try:
        stats = fifo_optimizado._stats.copy()

        # Estadísticas adicionales
        with fifo_optimizado._lock:
            cache_size = len(fifo_optimizado._cache_lotes)
            cache_keys = list(fifo_optimizado._cache_lotes.keys())

        # Estadísticas de base de datos
        total_lotes = LoteInventario.query.count()
        lotes_disponibles = LoteInventario.query.filter(
            LoteInventario.cantidad_disponible > 0
        ).count()

        return jsonify(
            {
                "status": "success",
                "fifo_optimizado_stats": stats,
                "cache_info": {
                    "cache_size": cache_size,
                    "cached_items": cache_keys[:10],  # Solo mostrar primeros 10
                },
                "database_info": {
                    "total_lotes": total_lotes,
                    "lotes_disponibles": lotes_disponibles,
                    "porcentaje_disponible": round(
                        (
                            (lotes_disponibles / total_lotes * 100)
                            if total_lotes > 0
                            else 0
                        ),
                        2,
                    ),
                },
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Error obteniendo estadísticas: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@fifo_optimizado_bp.route("/cache/clear", methods=["POST"])
@performance_monitor("fifo_cache_clear")
def limpiar_cache_fifo():
    """Limpiar cache del sistema FIFO"""
    try:
        with fifo_optimizado._lock:
            cache_size_antes = len(fifo_optimizado._cache_lotes)
            fifo_optimizado._cache_lotes.clear()

        return jsonify(
            {
                "status": "success",
                "message": f"Cache FIFO limpiado: {cache_size_antes} entradas eliminadas",
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Error limpiando cache: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )
