from app.models.plan_mantenimiento import PlanMantenimiento
from app.extensions import db
from datetime import datetime, timedelta


def listar_planes():
    planes = PlanMantenimiento.query.all()
    return [
        {
            "id": p.id,
            "codigo_plan": p.codigo_plan,
            "nombre": p.nombre,
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
            "activo": p.activo.nombre if p.activo else None,
        }
        for p in planes
    ]


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
