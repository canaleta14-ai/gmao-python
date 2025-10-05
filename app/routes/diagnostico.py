from flask import Blueprint, jsonify
from app.models.plan_mantenimiento import PlanMantenimiento
from datetime import datetime

diagnostico_bp = Blueprint("diagnostico", __name__, url_prefix="/diagnostico")


@diagnostico_bp.route("/planes-debug", methods=["GET"])
def planes_debug():
    """Endpoint de diagnóstico para ver exactamente qué está pasando con los planes"""

    ahora = datetime.now()

    # Obtener todos los planes activos
    todos_planes = PlanMantenimiento.query.filter(
        PlanMantenimiento.estado == "Activo"
    ).all()

    resultado = {
        "fecha_hora_servidor": ahora.isoformat(),
        "total_planes_activos": len(todos_planes),
        "planes": [],
    }

    for plan in todos_planes:
        plan_info = {
            "id": plan.id,
            "codigo": plan.codigo_plan,
            "nombre": plan.nombre,
            "estado": plan.estado,
            "proxima_ejecucion": (
                plan.proxima_ejecucion.isoformat() if plan.proxima_ejecucion else None
            ),
            "generacion_automatica": plan.generacion_automatica,
            "activo_id": plan.activo_id,
            "comparaciones": {},
        }

        if plan.proxima_ejecucion:
            plan_info["comparaciones"]["vencido"] = plan.proxima_ejecucion <= ahora
            plan_info["comparaciones"]["diferencia_horas"] = (
                ahora - plan.proxima_ejecucion
            ).total_seconds() / 3600

        # Verificar todas las condiciones
        cumple_estado = plan.estado == "Activo"
        cumple_fecha = (
            plan.proxima_ejecucion <= ahora if plan.proxima_ejecucion else False
        )
        cumple_generacion = plan.generacion_automatica == True

        plan_info["condiciones"] = {
            "estado_activo": cumple_estado,
            "fecha_vencida": cumple_fecha,
            "generacion_automatica_true": cumple_generacion,
            "debe_generar": cumple_estado and cumple_fecha and cumple_generacion,
        }

        resultado["planes"].append(plan_info)

    # Contar cuántos planes deberían generar
    planes_que_deberian_generar = [
        p for p in resultado["planes"] if p["condiciones"]["debe_generar"]
    ]
    resultado["planes_que_deberian_generar"] = len(planes_que_deberian_generar)

    return jsonify(resultado)
