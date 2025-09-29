from datetime import datetime

print("Verificación de fechas:")
print(f"28/9/2025 (hoy): {datetime(2025, 9, 28).strftime('%A')}")
print(f"29/9/2025: {datetime(2025, 9, 29).strftime('%A')}")
print(f"30/9/2025: {datetime(2025, 9, 30).strftime('%A')}")

# Verificar el plan semanal
from app import create_app
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.orden_trabajo import OrdenTrabajo

app = create_app()
with app.app_context():
    # Buscar plan semanal
    plan_semanal = PlanMantenimiento.query.filter(
        PlanMantenimiento.frecuencia.contains("Semanal")
    ).first()

    if plan_semanal:
        print(f"\nPlan encontrado: {plan_semanal.codigo_plan}")
        print(f"Próxima ejecución: {plan_semanal.proxima_ejecucion}")
        print(f"Día programado: {plan_semanal.proxima_ejecucion.strftime('%A')}")

    # Buscar órdenes de septiembre
    ordenes_sept = OrdenTrabajo.query.filter(
        OrdenTrabajo.fecha_programada >= datetime(2025, 9, 1),
        OrdenTrabajo.fecha_programada <= datetime(2025, 9, 30),
    ).all()

    print(f"\nÓrdenes de septiembre: {len(ordenes_sept)}")
    for orden in ordenes_sept:
        fecha_str = (
            orden.fecha_programada.strftime("%Y-%m-%d %A")
            if orden.fecha_programada
            else "Sin fecha"
        )
        print(f"  {orden.numero_orden}: {fecha_str} - {orden.descripcion[:50]}")
