from app.models.plan_mantenimiento import PlanMantenimiento
from app.extensions import db
from datetime import datetime, timedelta
from flask import request


def listar_planes():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    search = request.args.get("q", "", type=str)

    query = PlanMantenimiento.query

    # Aplicar filtros de búsqueda
    if search:
        query = query.filter(
            db.or_(
                PlanMantenimiento.codigo_plan.ilike(f"%{search}%"),
                PlanMantenimiento.nombre.ilike(f"%{search}%"),
                PlanMantenimiento.frecuencia.ilike(f"%{search}%"),
            )
        )

    # Paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    planes = pagination.items

    planes_data = [
        {
            "id": p.id,
            "codigo": p.codigo_plan,
            "nombre": p.nombre,
            "equipo": p.activo.nombre if p.activo else "Sin asignar",
            "frecuencia": p.frecuencia,
            "ultima_ejecucion": (
                p.ultima_ejecucion.strftime("%d/%m/%Y") if p.ultima_ejecucion else None
            ),
            "proxima_ejecucion": (
                p.proxima_ejecucion.strftime("%d/%m/%Y")
                if p.proxima_ejecucion
                else None
            ),
            "estado": p.estado,
        }
        for p in planes
    ]

    return {
        "items": planes_data,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }


def crear_plan(data):
    frecuencias_dias = {
        "Diario": 1,
        "Semanal": 7,
        "Quincenal": 15,
        "Mensual": 30,
        "Trimestral": 90,
        "Anual": 365,
    }
    dias = frecuencias_dias.get(data["frecuencia"], 30)
    proxima_ejecucion = datetime.utcnow() + timedelta(days=dias)
    nuevo_plan = PlanMantenimiento(
        codigo_plan=data["codigo_plan"],
        nombre=data["nombre"],
        frecuencia=data["frecuencia"],
        frecuencia_dias=dias,
        proxima_ejecucion=proxima_ejecucion,
        estado="Activo",
        descripcion=data.get("descripcion"),
        instrucciones=data.get("instrucciones"),
        tiempo_estimado=data.get("tiempo_estimado"),
        activo_id=data.get("activo_id"),
    )
    db.session.add(nuevo_plan)
    db.session.commit()
    return nuevo_plan
