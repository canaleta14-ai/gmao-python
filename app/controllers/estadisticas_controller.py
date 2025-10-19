from app.models.orden_trabajo import OrdenTrabajo
from app.models.activo import Activo
from app.models.lote_inventario import LoteInventario
from app.models.inventario import Inventario
from app.extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func


def obtener_estadisticas():
    # Obtener conteos por estado de órdenes
    ordenes_estado = (
        db.session.query(OrdenTrabajo.estado, db.func.count(OrdenTrabajo.id))
        .group_by(OrdenTrabajo.estado)
        .all()
    )
    ordenes_por_estado = dict(ordenes_estado)

    # Calcular órdenes de la última semana
    fecha_inicio = datetime.utcnow() - timedelta(days=7)
    ordenes_semana = OrdenTrabajo.query.filter(
        OrdenTrabajo.fecha_creacion >= fecha_inicio
    ).count()

    # Obtener conteos por estado de activos
    activos_estado = (
        db.session.query(Activo.estado, db.func.count(Activo.id))
        .group_by(Activo.estado)
        .all()
    )
    activos_por_estado = dict(activos_estado)

    # Calcular total de activos
    total_activos = sum(activos_por_estado.values())

    # ================== ESTADÍSTICAS FIFO ==================
    try:
        # Total de lotes en el sistema
        total_lotes = LoteInventario.query.count()

        # Lotes con stock disponible
        lotes_disponibles = LoteInventario.query.filter(
            LoteInventario.cantidad_actual > 0
        ).count()

        # Artículos con lotes FIFO
        articulos_con_lotes = (
            db.session.query(
                func.count(func.distinct(LoteInventario.inventario_id))
            ).scalar()
            or 0
        )

        # Total de artículos en inventario
        total_articulos = Inventario.query.count()

        # Lotes próximos a vencer (próximos 30 días)
        fecha_limite = datetime.utcnow() + timedelta(days=30)
        lotes_proximos_vencer = LoteInventario.query.filter(
            LoteInventario.fecha_vencimiento.isnot(None),
            LoteInventario.fecha_vencimiento <= fecha_limite,
            LoteInventario.fecha_vencimiento >= datetime.utcnow(),
            LoteInventario.cantidad_actual > 0,
        ).count()

        # Lotes vencidos
        lotes_vencidos = LoteInventario.query.filter(
            LoteInventario.fecha_vencimiento.isnot(None),
            LoteInventario.fecha_vencimiento < datetime.utcnow(),
            LoteInventario.cantidad_actual > 0,
        ).count()

        # Valor total del inventario en lotes
        valor_total = (
            db.session.query(
                func.sum(
                    LoteInventario.cantidad_actual * LoteInventario.precio_unitario
                )
            ).scalar()
            or 0
        )

        fifo_stats = {
            "total_lotes": total_lotes,
            "lotes_disponibles": lotes_disponibles,
            "articulos_con_lotes": articulos_con_lotes,
            "total_articulos": total_articulos,
            "lotes_proximos_vencer": lotes_proximos_vencer,
            "lotes_vencidos": lotes_vencidos,
            "valor_total_inventario": float(valor_total),
            "porcentaje_cobertura": round(
                (
                    (articulos_con_lotes / total_articulos * 100)
                    if total_articulos > 0
                    else 0
                ),
                1,
            ),
        }
    except Exception as e:
        # Si hay error en estadísticas FIFO, devolver valores por defecto
        print(f"Error obteniendo estadísticas FIFO: {e}")
        fifo_stats = {
            "total_lotes": 0,
            "lotes_disponibles": 0,
            "articulos_con_lotes": 0,
            "total_articulos": 0,
            "lotes_proximos_vencer": 0,
            "lotes_vencidos": 0,
            "valor_total_inventario": 0,
            "porcentaje_cobertura": 0,
        }

    return {
        "ordenes_por_estado": ordenes_por_estado,
        "ordenes_ultima_semana": ordenes_semana,
        "activos_por_estado": activos_por_estado,
        "total_activos": total_activos,
        "fifo_stats": fifo_stats,
    }
