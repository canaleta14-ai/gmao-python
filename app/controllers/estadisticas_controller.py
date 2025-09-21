from app.models.orden_trabajo import OrdenTrabajo
from app.models.activo import Activo
from app.extensions import db
from datetime import datetime, timedelta


def obtener_estadisticas():
    ordenes_estado = (
        db.session.query(OrdenTrabajo.estado, db.func.count(OrdenTrabajo.id))
        .group_by(OrdenTrabajo.estado)
        .all()
    )
    fecha_inicio = datetime.utcnow() - timedelta(days=7)
    ordenes_semana = OrdenTrabajo.query.filter(
        OrdenTrabajo.fecha_creacion >= fecha_inicio
    ).count()
    activos_estado = (
        db.session.query(Activo.estado, db.func.count(Activo.id))
        .group_by(Activo.estado)
        .all()
    )
    return {
        "ordenes_por_estado": dict(ordenes_estado),
        "ordenes_ultima_semana": ordenes_semana,
        "activos_por_estado": dict(activos_estado),
    }
