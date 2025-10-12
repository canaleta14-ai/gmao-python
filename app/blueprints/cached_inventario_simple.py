#!/usr/bin/env python3
"""
🚀 BLUEPRINT DE ENDPOINTS CON CACHE SIMPLE
Para registrar en la aplicación principal
"""

from flask import Blueprint, jsonify, request
from app.models.inventario import Inventario
from app.models.lote_inventario import LoteInventario
from app.extensions import db
from sqlalchemy import func
import time
import json
import hashlib
from datetime import datetime

# Sistema de caché simple en memoria para desarrollo
_cache = {}
_cache_ttl = {}


def simple_cache(key, value=None, ttl=300):
    """Sistema de caché simple para desarrollo"""
    if value is not None:
        # Set value
        _cache[key] = value
        _cache_ttl[key] = datetime.now().timestamp() + ttl
        return True
    else:
        # Get value
        if key in _cache:
            if datetime.now().timestamp() < _cache_ttl.get(key, 0):
                return _cache[key]
            else:
                # Expired
                _cache.pop(key, None)
                _cache_ttl.pop(key, None)
        return None


def cache_key(*args):
    """Generar clave de caché"""
    return hashlib.md5(str(args).encode()).hexdigest()


# Crear blueprint para endpoints optimizados
cached_inventario_bp = Blueprint(
    "cached_inventario", __name__, url_prefix="/api/cached"
)


@cached_inventario_bp.route("/inventario/stats")
def get_inventario_stats():
    """Estadísticas de inventario con caché de 5 minutos"""
    cache_key_str = cache_key("inventario_stats")
    cached_result = simple_cache(cache_key_str)

    if cached_result is not None:
        cached_result["from_cache"] = True
        return jsonify(cached_result)

    # Calcular estadísticas
    total_inventarios = Inventario.query.count()
    total_lotes = LoteInventario.query.filter(
        LoteInventario.activo == True, LoteInventario.cantidad_actual > 0
    ).count()

    stock_total = (
        db.session.query(func.sum(LoteInventario.cantidad_actual))
        .filter(LoteInventario.activo == True, LoteInventario.cantidad_actual > 0)
        .scalar()
        or 0
    )

    # Valor total estimado
    valor_total = (
        db.session.query(
            func.sum(LoteInventario.cantidad_actual * LoteInventario.precio_unitario)
        )
        .filter(
            LoteInventario.activo == True,
            LoteInventario.cantidad_actual > 0,
            LoteInventario.precio_unitario.isnot(None),
        )
        .scalar()
        or 0
    )

    # Artículos con bajo stock
    articulos_bajo_stock = Inventario.query.filter(
        Inventario.stock_actual <= Inventario.stock_minimo, Inventario.stock_actual > 0
    ).count()

    result = {
        "total_inventarios": total_inventarios,
        "total_lotes": total_lotes,
        "stock_total": float(stock_total),
        "valor_total": float(valor_total),
        "articulos_bajo_stock": articulos_bajo_stock,
        "from_cache": False,
    }

    # Guardar en caché
    simple_cache(cache_key_str, result, ttl=300)

    return jsonify(result)


@cached_inventario_bp.route("/inventario/<int:inventario_id>/stock")
def get_inventario_stock(inventario_id):
    """Stock de inventario específico con caché de 2 minutos"""
    cache_key_str = cache_key("inventario_stock", inventario_id)
    cached_result = simple_cache(cache_key_str)

    if cached_result is not None:
        cached_result["from_cache"] = True
        return jsonify(cached_result)

    inventario = Inventario.query.get_or_404(inventario_id)

    lotes = (
        LoteInventario.query.filter(
            LoteInventario.inventario_id == inventario_id,
            LoteInventario.cantidad_actual > 0,
            LoteInventario.activo == True,
        )
        .order_by(LoteInventario.fecha_entrada.asc())
        .all()
    )

    result = {
        "inventario_id": inventario_id,
        "codigo": inventario.codigo,
        "descripcion": inventario.descripcion,
        "stock_total": sum(lote.cantidad_actual for lote in lotes),
        "lotes_count": len(lotes),
        "lotes": [
            {
                "id": lote.id,
                "codigo_lote": lote.codigo_lote,
                "cantidad_actual": lote.cantidad_actual,
                "fecha_entrada": (
                    lote.fecha_entrada.isoformat() if lote.fecha_entrada else None
                ),
                "fecha_vencimiento": (
                    lote.fecha_vencimiento.isoformat()
                    if lote.fecha_vencimiento
                    else None
                ),
            }
            for lote in lotes[:5]  # Primeros 5 lotes
        ],
        "from_cache": False,
    }

    # Guardar en caché
    simple_cache(cache_key_str, result, ttl=120)

    return jsonify(result)


@cached_inventario_bp.route("/inventario/<int:inventario_id>/fifo/<int:cantidad>")
def get_lotes_fifo(inventario_id, cantidad):
    """Obtener lotes en orden FIFO con caché de 1 minuto"""
    cache_key_str = cache_key("lotes_fifo", inventario_id, cantidad)
    cached_result = simple_cache(cache_key_str)

    if cached_result is not None:
        cached_result["from_cache"] = True
        return jsonify(cached_result)

    # Obtener lotes disponibles ordenados por FIFO
    lotes = (
        LoteInventario.query.filter(
            LoteInventario.inventario_id == inventario_id,
            LoteInventario.cantidad_actual > 0,
            LoteInventario.activo == True,
        )
        .order_by(LoteInventario.fecha_entrada.asc(), LoteInventario.id.asc())
        .all()
    )

    lotes_seleccionados = []
    cantidad_restante = cantidad

    for lote in lotes:
        if cantidad_restante <= 0:
            break

        cantidad_a_usar = min(lote.cantidad_actual, cantidad_restante)
        lotes_seleccionados.append(
            {
                "lote_id": lote.id,
                "codigo_lote": lote.codigo_lote,
                "cantidad_disponible": lote.cantidad_actual,
                "cantidad_a_usar": cantidad_a_usar,
                "fecha_entrada": (
                    lote.fecha_entrada.isoformat() if lote.fecha_entrada else None
                ),
                "precio_unitario": (
                    float(lote.precio_unitario) if lote.precio_unitario else 0.0
                ),
            }
        )

        cantidad_restante -= cantidad_a_usar

    result = {
        "inventario_id": inventario_id,
        "cantidad_requerida": cantidad,
        "cantidad_disponible": sum(
            lote["cantidad_a_usar"] for lote in lotes_seleccionados
        ),
        "lotes_fifo": lotes_seleccionados,
        "satisface_demanda": cantidad_restante <= 0,
        "from_cache": False,
    }

    # Guardar en caché
    simple_cache(cache_key_str, result, ttl=60)

    return jsonify(result)


# Endpoints de gestión de caché
@cached_inventario_bp.route("/cache/stats")
def get_cache_stats():
    """Estadísticas del sistema de caché simple"""
    total_keys = len(_cache)
    expired_keys = 0
    current_time = datetime.now().timestamp()

    for key, expiry in _cache_ttl.items():
        if current_time > expiry:
            expired_keys += 1

    return jsonify(
        {
            "total_keys": total_keys,
            "expired_keys": expired_keys,
            "active_keys": total_keys - expired_keys,
            "cache_type": "simple_memory",
        }
    )


@cached_inventario_bp.route("/cache/clear", methods=["POST"])
def clear_cache():
    """Limpiar todo el caché"""
    _cache.clear()
    _cache_ttl.clear()
    return jsonify({"message": "Cache cleared successfully", "keys_cleared": "all"})


@cached_inventario_bp.route("/test")
def test_endpoint():
    """Endpoint de prueba para verificar que el blueprint funciona"""
    return jsonify(
        {
            "message": "Blueprint de caché funcionando correctamente",
            "timestamp": datetime.now().isoformat(),
            "cache_keys": len(_cache),
        }
    )
