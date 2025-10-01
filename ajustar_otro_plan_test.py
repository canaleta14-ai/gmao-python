"""Script para ajustar otro plan y tener un candidato sin orden pendiente"""

from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.orden_trabajo import OrdenTrabajo
from app.extensions import db
from app import create_app
from datetime import datetime, timedelta

# Crear contexto de aplicación
app = create_app()
app.app_context().push()

print("=" * 70)
print("BUSCANDO PLAN SIN ORDEN PENDIENTE PARA PROBAR GENERACIÓN")
print("=" * 70)

# Buscar todos los planes activos sin generación automática
planes = PlanMantenimiento.query.filter_by(
    estado="Activo", generacion_automatica=False
).all()

print(f"\n📋 Total de planes candidatos: {len(planes)}")

plan_seleccionado = None

for plan in planes:
    # Verificar si tiene orden pendiente
    orden_existente = OrdenTrabajo.query.filter(
        OrdenTrabajo.tipo == "Mantenimiento Preventivo",
        OrdenTrabajo.activo_id == plan.activo_id,
        OrdenTrabajo.descripcion.contains(f"Plan: {plan.codigo_plan}"),
        OrdenTrabajo.estado.in_(["Pendiente", "En Proceso"]),
    ).first()

    if not orden_existente:
        plan_seleccionado = plan
        print(f"\n✅ Encontrado plan sin orden pendiente:")
        print(f"   Plan: {plan.nombre} ({plan.codigo_plan})")
        print(f"   Próxima ejecución actual: {plan.proxima_ejecucion}")
        break
    else:
        print(
            f"\n⚠️  Plan {plan.codigo_plan} ya tiene orden: {orden_existente.numero_orden}"
        )

if not plan_seleccionado:
    print("\n❌ Todos los planes ya tienen órdenes pendientes")
    print("   No hay nada que generar (sistema funcionando correctamente)")
    exit(0)

# Ajustar la fecha a ayer
ayer = datetime.now() - timedelta(days=1)
plan_seleccionado.proxima_ejecucion = ayer

print(f"   📅 Nueva próxima ejecución: {plan_seleccionado.proxima_ejecucion}")

# Guardar cambios
db.session.commit()

print("\n✅ Fecha actualizada exitosamente")
print(f"\n💡 Ahora puedes probar la generación manual desde la interfaz")
print(
    f"   El plan '{plan_seleccionado.nombre}' ({plan_seleccionado.codigo_plan}) debería generar una orden"
)

print("\n" + "=" * 70)
