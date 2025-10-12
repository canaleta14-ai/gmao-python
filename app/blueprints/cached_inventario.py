#!/usr/bin/env python3
"""
🚀 BLUEPRINT DE ENDPOINTS CON CACHE
Para registrar en la aplicación principal
"""

from flask import Blueprint, jsonify, request
import cache_system
from app.models.inventario import Inventario
from app.models.lote_inventario import LoteInventario
from app.extensions import db
from sqlalchemy import func, desc

# Crear blueprint para endpoints optimizados
cached_inventario_bp = Blueprint(
    "cached_inventario", __name__, url_prefix="/api/cached"
)


@cached_inventario_bp.route("/inventario/stats")
@cache_system.cached_fifo_operation("inventario_stats", ttl=300)
def get_inventario_stats():
    """Estadísticas de inventario con caché de 5 minutos"""
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

    return jsonify(
        {
            "total_inventarios": total_inventarios,
            "total_lotes": total_lotes,
            "stock_total": float(stock_total),
            "valor_total": float(valor_total),
            "articulos_bajo_stock": articulos_bajo_stock,
            "cached": True,
        }
    )


@cached_inventario_bp.route("/inventario/<int:inventario_id>/stock")
@cache_system.cached_fifo_operation("inventario_stock", ttl=120)
def get_inventario_stock(inventario_id):
    """Stock de inventario específico con caché de 2 minutos"""
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

    return jsonify(
        {
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
            "cached": True,
        }
    )


@cached_inventario_bp.route("/inventario/<int:inventario_id>/fifo/<int:cantidad>")
@cache_system.cached_fifo_operation("lotes_fifo", ttl=60)
def get_lotes_fifo(inventario_id, cantidad):
    """Obtener lotes en orden FIFO con caché de 1 minuto"""
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

    return jsonify(
        {
            "inventario_id": inventario_id,
            "cantidad_requerida": cantidad,
            "cantidad_disponible": sum(
                lote["cantidad_a_usar"] for lote in lotes_seleccionados
            ),
            "lotes_fifo": lotes_seleccionados,
            "satisface_demanda": cantidad_restante <= 0,
            "cached": True,
        }
    )


@cached_inventario_bp.route("/inventario/list")
@cache_system.cached_fifo_operation("inventario_list", ttl=180)
def get_inventario_list():
    """Lista de inventarios con caché de 3 minutos"""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)  # Max 100 items
    search = request.args.get("q", "", type=str)

    query = Inventario.query

    # Aplicar filtros de búsqueda
    if search:
        query = query.filter(
            db.or_(
                Inventario.codigo.ilike(f"%{search}%"),
                Inventario.descripcion.ilike(f"%{search}%"),
                Inventario.categoria.ilike(f"%{search}%"),
            )
        )

    # Paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(
        {
            "items": [
                {
                    "id": item.id,
                    "codigo": item.codigo,
                    "descripcion": item.descripcion,
                    "categoria": item.categoria,
                    "stock_actual": item.stock_actual,
                    "stock_minimo": item.stock_minimo,
                    "precio_unitario": (
                        float(item.precio_unitario) if item.precio_unitario else 0.0
                    ),
                }
                for item in pagination.items
            ],
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            },
            "cached": True,
        }
    )


# Endpoints de gestión de caché
@cached_inventario_bp.route("/cache/stats")
def get_cache_stats():
    """Estadísticas del sistema de caché"""
    stats = cache_system.cache_manager.get_stats()
    return jsonify(
        {
            "hits": stats.hits,
            "misses": stats.misses,
            "total_requests": stats.total_requests,
            "hit_ratio": round(stats.hit_ratio, 2),
            "cache_size": stats.cache_size,
            "average_time_saved": round(stats.average_time_saved * 1000, 3),  # en ms
            "last_reset": stats.last_reset.isoformat() if stats.last_reset else None,
        }
    )


@cached_inventario_bp.route("/cache/clear", methods=["POST"])
def clear_cache():
    """Limpiar todo el caché"""
    cache_system.cache_manager.clear_all()
    return jsonify({"message": "Cache cleared successfully"})


@cached_inventario_bp.route("/cache/invalidate/<pattern>", methods=["POST"])
def invalidate_cache_pattern(pattern):
    """Invalidar caché por patrón"""
    cache_system.cache_manager.invalidate_pattern(pattern)
    return jsonify({"message": f"Cache pattern '{pattern}' invalidated"})


# Funciones utilitarias para invalidación automática
def invalidate_inventario_cache(inventario_id=None):
    """Invalidar caché relacionado con inventario específico"""
    if inventario_id:
        patterns = [
            f"fifo_cache:inventario_stock:*{inventario_id}*",
            f"fifo_cache:lotes_fifo:*{inventario_id}*",
            "fifo_cache:inventario_stats:*",
            "fifo_cache:inventario_list:*",
        ]
        for pattern in patterns:
            cache_system.cache_manager.invalidate_pattern(pattern)
    else:
        # Invalidar todo el caché de inventario
        cache_system.cache_manager.invalidate_pattern("fifo_cache:inventario*")


def warm_up_cache():
    """Precalentar caché con datos frecuentemente consultados"""
    try:
        # Estadísticas generales
        get_inventario_stats()

        # Primeros inventarios PERF (más consultados)
        inventarios_perf = (
            Inventario.query.filter(Inventario.codigo.like("PERF-%")).limit(10).all()
        )

        for inv in inventarios_perf:
            get_inventario_stock(inv.id)
            get_lotes_fifo(inv.id, 100)  # Cantidad típica

        return len(inventarios_perf)

    except Exception as e:
        print(f"Error precalentando cache: {e}")
        return 0
