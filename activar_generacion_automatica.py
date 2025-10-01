"""Script para activar generación automática en un plan y probarlo"""

from app.models.plan_mantenimiento import PlanMantenimiento
from app.extensions import db
from app import create_app
from datetime import datetime, timedelta

# Crear contexto de aplicación
app = create_app()
app.app_context().push()

print("=" * 80)
print("CONFIGURANDO PLAN PARA GENERACIÓN AUTOMÁTICA")
print("=" * 80)

# Buscar el plan PM-2025-0003 (que está en fecha futura)
plan = PlanMantenimiento.query.filter_by(codigo_plan="PM-2025-0003").first()

if not plan:
    print("❌ No se encontró el plan PM-2025-0003")
    exit(1)

print(f"\n📋 Plan seleccionado: {plan.nombre} ({plan.codigo_plan})")
print(f"   Estado actual: {plan.estado}")
print(f"   Generación automática actual: {plan.generacion_automatica}")
print(f"   Próxima ejecución actual: {plan.proxima_ejecucion}")

# Activar generación automática
plan.generacion_automatica = True

# Ajustar la fecha a ayer para que esté vencido
ayer = datetime.now() - timedelta(days=1)
plan.proxima_ejecucion = ayer

print(f"\n🔄 CAMBIOS APLICADOS:")
print(f"   ✅ Generación automática: {plan.generacion_automatica}")
print(f"   ✅ Nueva próxima ejecución: {plan.proxima_ejecucion}")

# Guardar cambios
db.session.commit()

print("\n✅ Plan actualizado exitosamente")

# Verificar que ahora es candidato
ahora = datetime.now()
es_candidato = (
    plan.estado == "Activo"
    and plan.generacion_automatica == True
    and plan.proxima_ejecucion <= ahora
)

print("\n" + "=" * 80)
print("VERIFICACIÓN")
print("=" * 80)

if es_candidato:
    print(f"✅ El plan '{plan.nombre}' AHORA ES CANDIDATO para generación AUTOMÁTICA")
    print(f"\n💡 Puedes probar la generación automática:")
    print(f"   1. Ejecuta: python scheduler_simple.py --test")
    print(f"   2. O espera a que se ejecute automáticamente a las 6:00 AM")
    print(f"   3. O ve al calendario: http://localhost:5000/calendario")
else:
    print(f"❌ El plan '{plan.nombre}' AÚN NO es candidato")

print("=" * 80)
