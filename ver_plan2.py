from app import create_app
from app.models.plan_mantenimiento import PlanMantenimiento

app = create_app()

with app.app_context():
    plan = PlanMantenimiento.query.filter_by(codigo_plan="PM-2025-0001").first()
    if plan:
        print(f"Plan: {plan.codigo_plan} - {plan.nombre}")
        print(f"Estado: {plan.estado}")
        print(f"Frecuencia: {plan.frecuencia} ({plan.frecuencia_dias} días)")
        print(f"Última ejecución: {plan.ultima_ejecucion}")
        print(f"Próxima ejecución: {plan.proxima_ejecucion}")
        print(f"Activo asociado: {plan.activo_id}")
    else:
        print("Plan no encontrado")
