"""Script para ajustar fechas de planes y probar generación manual"""

from app.models.plan_mantenimiento import PlanMantenimiento
from app.extensions import db
from app import create_app
from datetime import datetime, timedelta

# Crear contexto de aplicación
app = create_app()
app.app_context().push()

print("=" * 70)
print("AJUSTANDO FECHAS PARA PRUEBA DE GENERACIÓN MANUAL")
print("=" * 70)

# Buscar el primer plan activo sin generación automática
plan = PlanMantenimiento.query.filter_by(
    estado="Activo", generacion_automatica=False
).first()

if not plan:
    print("❌ No se encontró ningún plan activo sin generación automática")
    exit(1)

print(f"\n📋 Plan seleccionado: {plan.nombre} ({plan.codigo_plan})")
print(f"   Próxima ejecución actual: {plan.proxima_ejecucion}")

# Ajustar la fecha a ayer (para que esté vencido)
ayer = datetime.now() - timedelta(days=1)
fecha_anterior = plan.proxima_ejecucion
plan.proxima_ejecucion = ayer

print(f"   📅 Nueva próxima ejecución: {plan.proxima_ejecucion}")

# Guardar cambios
db.session.commit()

print("\n✅ Fecha actualizada exitosamente")
print(f"\n💡 Ahora puedes probar la generación manual desde la interfaz")
print(f"   El plan '{plan.nombre}' debería aparecer como candidato")

print("\n" + "=" * 70)
print("VERIFICACIÓN")
print("=" * 70)

# Verificar que el plan ahora es candidato
ahora = datetime.now()
fecha_objetivo = ahora + timedelta(days=1)

es_candidato = (
    plan.estado == "Activo"
    and plan.generacion_automatica == False
    and plan.proxima_ejecucion <= fecha_objetivo
)

if es_candidato:
    print(f"✅ El plan '{plan.nombre}' AHORA ES CANDIDATO para generación manual")
else:
    print(f"❌ El plan '{plan.nombre}' AÚN NO es candidato (algo salió mal)")

print("=" * 70)
