from app import create_app
from app.models.plan_mantenimiento import PlanMantenimiento

app = create_app()
with app.app_context():
    # Buscar el plan semanal específico
    plan = PlanMantenimiento.query.filter(
        PlanMantenimiento.codigo_plan.contains("SEMANAL")
    ).first()

    if not plan:
        plan = PlanMantenimiento.query.filter(
            PlanMantenimiento.descripcion.contains("Lunes")
        ).first()

    if not plan:
        # Buscar por frecuencia
        plan = PlanMantenimiento.query.filter(
            PlanMantenimiento.tipo_frecuencia == "semanal"
        ).first()

    if plan:
        print(f"Plan encontrado: {plan.codigo_plan}")
        print(f"Nombre: {plan.nombre}")
        print(f"Tipo frecuencia: {plan.tipo_frecuencia}")
        print(f"Días semana: {plan.dias_semana}")
        print(f"Interval semanas: {plan.intervalo_semanas}")
        print(f"Próxima ejecución: {plan.proxima_ejecucion}")
        print(
            f"Día programado: {plan.proxima_ejecucion.strftime('%A') if plan.proxima_ejecucion else 'Sin fecha'}"
        )

        # Verificar si hay configuración incorrecta
        if plan.dias_semana:
            import json

            try:
                dias = json.loads(plan.dias_semana)
                print(f"Días configurados: {dias}")
            except:
                print(f"Días configurados (string): {plan.dias_semana}")
    else:
        print("No se encontró plan semanal")

        # Listar todos los planes
        todos_planes = PlanMantenimiento.query.all()
        print(f"\nTodos los planes ({len(todos_planes)}):")
        for p in todos_planes:
            print(f"  {p.codigo_plan}: {p.tipo_frecuencia} - {p.proxima_ejecucion}")
