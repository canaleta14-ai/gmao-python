from app.models.orden_trabajo import OrdenTrabajo
from app.models.activo import Activo
from app.models.usuario import Usuario
from app.extensions import db
from datetime import datetime, timezone
import csv
import io


def listar_ordenes(estado=None, limit=None):
    """Listar órdenes de trabajo con filtro opcional por estado y límite"""
    query = OrdenTrabajo.query

    if estado:
        query = query.filter_by(estado=estado)

    query = query.order_by(OrdenTrabajo.fecha_creacion.desc())

    if limit:
        try:
            query = query.limit(int(limit))
        except ValueError:
            pass  # Ignorar límite inválido

    ordenes = query.all()

    return [
        {
            "id": o.id,
            "numero_orden": o.numero_orden,
            "fecha_creacion": (
                o.fecha_creacion.strftime("%d/%m/%Y %H:%M")
                if o.fecha_creacion
                else None
            ),
            "fecha_programada": (
                o.fecha_programada.strftime("%d/%m/%Y") if o.fecha_programada else None
            ),
            "fecha_completada": (
                o.fecha_completada.strftime("%d/%m/%Y %H:%M")
                if o.fecha_completada
                else None
            ),
            "tipo": o.tipo,
            "prioridad": o.prioridad,
            "estado": o.estado,
            "descripcion": o.descripcion,
            "observaciones": o.observaciones,
            "tiempo_estimado": o.tiempo_estimado,
            "tiempo_real": o.tiempo_real,
            "activo_id": o.activo_id,
            "activo_nombre": o.activo.nombre if o.activo else None,
            "activo_codigo": o.activo.codigo if o.activo else None,
            "tecnico_id": o.tecnico_id,
            "tecnico_nombre": o.tecnico.nombre if o.tecnico else None,
        }
        for o in ordenes
    ]


def obtener_orden(id):
    """Obtener una orden de trabajo específica"""
    orden = OrdenTrabajo.query.get_or_404(id)
    return {
        "id": orden.id,
        "numero_orden": orden.numero_orden,
        "fecha_creacion": (
            orden.fecha_creacion.strftime("%Y-%m-%dT%H:%M")
            if orden.fecha_creacion
            else None
        ),
        "fecha_programada": (
            orden.fecha_programada.strftime("%Y-%m-%d")
            if orden.fecha_programada
            else None
        ),
        "fecha_completada": (
            orden.fecha_completada.strftime("%Y-%m-%dT%H:%M")
            if orden.fecha_completada
            else None
        ),
        "tipo": orden.tipo,
        "prioridad": orden.prioridad,
        "estado": orden.estado,
        "descripcion": orden.descripcion,
        "observaciones": orden.observaciones,
        "tiempo_estimado": orden.tiempo_estimado,
        "tiempo_real": orden.tiempo_real,
        "activo_id": orden.activo_id,
        "tecnico_id": orden.tecnico_id,
    }


def crear_orden(data):
    """Crear nueva orden de trabajo"""
    # Generar número de orden único
    ultimo_numero = db.session.query(db.func.max(OrdenTrabajo.id)).scalar() or 0
    numero_orden = f"OT-{ultimo_numero + 1:06d}"

    # Validar que el activo existe si se proporciona
    if data.get("activo_id"):
        activo = Activo.query.get(data["activo_id"])
        if not activo:
            raise ValueError("El activo especificado no existe")

    # Validar que el técnico existe si se proporciona
    if data.get("tecnico_id"):
        tecnico = Usuario.query.get(data["tecnico_id"])
        if not tecnico:
            raise ValueError("El técnico especificado no existe")

    nueva_orden = OrdenTrabajo(
        numero_orden=numero_orden,
        tipo=data["tipo"],
        prioridad=data["prioridad"],
        estado="Pendiente",
        descripcion=data["descripcion"],
        observaciones=data.get("observaciones"),
        activo_id=data.get("activo_id"),
        tecnico_id=data.get("tecnico_id"),
        tiempo_estimado=(
            float(data.get("tiempo_estimado", 0))
            if data.get("tiempo_estimado")
            else None
        ),
    )

    # Procesar fecha programada
    if data.get("fecha_programada"):
        try:
            nueva_orden.fecha_programada = datetime.strptime(
                data["fecha_programada"], "%Y-%m-%d"
            )
        except ValueError:
            raise ValueError("Formato de fecha programada inválido. Use YYYY-MM-DD")

    db.session.add(nueva_orden)
    db.session.commit()
    return nueva_orden


def actualizar_orden(id, data):
    """Actualizar orden de trabajo existente"""
    orden = OrdenTrabajo.query.get_or_404(id)

    # Validar que el activo existe si se proporciona
    if data.get("activo_id") and data["activo_id"] != orden.activo_id:
        activo = Activo.query.get(data["activo_id"])
        if not activo:
            raise ValueError("El activo especificado no existe")

    # Validar que el técnico existe si se proporciona
    if data.get("tecnico_id") and data["tecnico_id"] != orden.tecnico_id:
        tecnico = Usuario.query.get(data["tecnico_id"])
        if not tecnico:
            raise ValueError("El técnico especificado no existe")

    # Actualizar campos
    orden.tipo = data.get("tipo", orden.tipo)
    orden.prioridad = data.get("prioridad", orden.prioridad)
    orden.descripcion = data.get("descripcion", orden.descripcion)
    orden.observaciones = data.get("observaciones", orden.observaciones)
    orden.activo_id = data.get("activo_id", orden.activo_id)
    orden.tecnico_id = data.get("tecnico_id", orden.tecnico_id)

    # Actualizar tiempo estimado
    if data.get("tiempo_estimado") is not None:
        orden.tiempo_estimado = (
            float(data["tiempo_estimado"]) if data["tiempo_estimado"] else None
        )

    # Procesar fecha programada
    if data.get("fecha_programada") is not None:
        if data["fecha_programada"]:
            try:
                orden.fecha_programada = datetime.strptime(
                    data["fecha_programada"], "%Y-%m-%d"
                )
            except ValueError:
                raise ValueError("Formato de fecha programada inválido. Use YYYY-MM-DD")
        else:
            orden.fecha_programada = None

    db.session.commit()
    return orden


def actualizar_estado_orden(id, data):
    """Actualizar estado de una orden de trabajo"""
    orden = OrdenTrabajo.query.get_or_404(id)

    estado_anterior = orden.estado
    nuevo_estado = data["estado"]

    # Validar transición de estado
    estados_validos = [
        "Pendiente",
        "En Proceso",
        "Completada",
        "Cancelada",
        "En Espera",
    ]
    if nuevo_estado not in estados_validos:
        raise ValueError(f"Estado '{nuevo_estado}' no válido")

    orden.estado = nuevo_estado

    # Lógica especial para estados específicos
    if nuevo_estado == "Completada" and estado_anterior != "Completada":
        orden.fecha_completada = datetime.now(timezone.utc)
        # Actualizar tiempo real si se proporciona
        if data.get("tiempo_real"):
            orden.tiempo_real = float(data["tiempo_real"])
    elif nuevo_estado != "Completada":
        # Si se cambia de Completada a otro estado, limpiar fecha de completado
        orden.fecha_completada = None

    # Actualizar observaciones si se proporcionan
    if data.get("observaciones"):
        orden.observaciones = data["observaciones"]

    db.session.commit()
    return orden


def eliminar_orden(id):
    """Eliminar orden de trabajo"""
    orden = OrdenTrabajo.query.get_or_404(id)

    # Solo permitir eliminar órdenes en estado Pendiente o Cancelada
    if orden.estado not in ["Pendiente", "Cancelada"]:
        raise ValueError(
            "Solo se pueden eliminar órdenes en estado 'Pendiente' o 'Cancelada'"
        )

    db.session.delete(orden)
    db.session.commit()
    return True


def obtener_activos_disponibles():
    """Obtener lista de activos para selección en órdenes"""
    activos = Activo.query.filter_by(estado="Operativo").order_by(Activo.codigo).all()
    return [
        {
            "id": activo.id,
            "codigo": activo.codigo,
            "nombre": activo.nombre,
            "ubicacion": activo.ubicacion,
            "display": f"{activo.codigo} - {activo.nombre}"
            + (f" ({activo.ubicacion})" if activo.ubicacion else ""),
        }
        for activo in activos
    ]


def obtener_tecnicos_disponibles():
    """Obtener lista de técnicos para asignación de órdenes"""
    tecnicos = (
        Usuario.query.filter_by(activo=True)
        .filter(Usuario.rol.in_(["Técnico", "Supervisor", "Administrador"]))
        .order_by(Usuario.nombre)
        .all()
    )

    return [
        {
            "id": tecnico.id,
            "nombre": tecnico.nombre,
            "rol": tecnico.rol,
            "display": f"{tecnico.nombre} ({tecnico.rol})",
        }
        for tecnico in tecnicos
    ]


def obtener_estadisticas_ordenes():
    """Obtener estadísticas de órdenes de trabajo"""
    from sqlalchemy import func, and_
    from datetime import date, timedelta

    # Contar por estado
    stats_estado = (
        db.session.query(OrdenTrabajo.estado, func.count(OrdenTrabajo.id))
        .group_by(OrdenTrabajo.estado)
        .all()
    )

    # Órdenes de esta semana
    inicio_semana = date.today() - timedelta(days=7)
    ordenes_semana = OrdenTrabajo.query.filter(
        OrdenTrabajo.fecha_creacion >= inicio_semana
    ).count()

    # Órdenes vencidas (programadas para antes de hoy y no completadas)
    hoy = date.today()
    ordenes_vencidas = OrdenTrabajo.query.filter(
        and_(OrdenTrabajo.fecha_programada < hoy, OrdenTrabajo.estado != "Completada")
    ).count()

    # Promedio de tiempo de resolución (últimas 30 órdenes completadas)
    ordenes_completadas = (
        OrdenTrabajo.query.filter_by(estado="Completada")
        .filter(OrdenTrabajo.tiempo_real.isnot(None))
        .order_by(OrdenTrabajo.fecha_completada.desc())
        .limit(30)
        .all()
    )

    tiempo_promedio = 0
    if ordenes_completadas:
        tiempo_total = sum(o.tiempo_real for o in ordenes_completadas)
        tiempo_promedio = tiempo_total / len(ordenes_completadas)

    return {
        "por_estado": dict(stats_estado),
        "ordenes_semana": ordenes_semana,
        "ordenes_vencidas": ordenes_vencidas,
        "tiempo_promedio_resolucion": round(tiempo_promedio, 2),
    }


def exportar_ordenes_csv():
    """Exportar órdenes de trabajo a CSV"""
    ordenes = OrdenTrabajo.query.order_by(OrdenTrabajo.fecha_creacion.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Encabezados
    writer.writerow(
        [
            "Número",
            "Fecha Creación",
            "Fecha Programada",
            "Fecha Completada",
            "Tipo",
            "Prioridad",
            "Estado",
            "Descripción",
            "Observaciones",
            "Tiempo Estimado",
            "Tiempo Real",
            "Activo",
            "Técnico",
        ]
    )

    # Datos
    for orden in ordenes:
        writer.writerow(
            [
                orden.numero_orden,
                (
                    orden.fecha_creacion.strftime("%d/%m/%Y %H:%M")
                    if orden.fecha_creacion
                    else ""
                ),
                (
                    orden.fecha_programada.strftime("%d/%m/%Y")
                    if orden.fecha_programada
                    else ""
                ),
                (
                    orden.fecha_completada.strftime("%d/%m/%Y %H:%M")
                    if orden.fecha_completada
                    else ""
                ),
                orden.tipo or "",
                orden.prioridad or "",
                orden.estado or "",
                orden.descripcion or "",
                orden.observaciones or "",
                orden.tiempo_estimado or "",
                orden.tiempo_real or "",
                orden.activo.nombre if orden.activo else "",
                orden.tecnico.nombre if orden.tecnico else "",
            ]
        )

    output.seek(0)
    return output.getvalue()
