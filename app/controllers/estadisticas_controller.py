from app.models.orden_trabajo import OrdenTrabajo
from app.models.activo import Activo
from app.extensions import db
from datetime import datetime, timedelta


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

    return {
        "ordenes_por_estado": ordenes_por_estado,
        "ordenes_ultima_semana": ordenes_semana,
        "activos_por_estado": activos_por_estado,
        "total_activos": total_activos,
    }
