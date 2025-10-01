"""Script para diagnosticar la generación manual de órdenes preventivas"""

from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.orden_trabajo import OrdenTrabajo
from app.extensions import db
from app import create_app
from datetime import datetime, timedelta

# Crear contexto de aplicación
app = create_app()
app.app_context().push()

print("=" * 70)
print("DIAGNÓSTICO: GENERACIÓN MANUAL DE ÓRDENES PREVENTIVAS")
print("=" * 70)

# 1. Verificar planes existentes
planes = PlanMantenimiento.query.all()
print(f"\n📋 TOTAL DE PLANES: {len(planes)}")
print("-" * 70)

if len(planes) == 0:
    print("❌ No hay planes de mantenimiento en la base de datos")
    exit(1)

# 2. Analizar cada plan
ahora = datetime.now()
fecha_objetivo = ahora + timedelta(days=1)

print(f"📅 Fecha actual: {ahora.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📅 Fecha objetivo (mañana): {fecha_objetivo.strftime('%Y-%m-%d %H:%M:%S')}")
print("-" * 70)

planes_activos = 0
planes_inactivos = 0
planes_con_auto = 0
planes_sin_auto = 0
planes_vencidos = 0
planes_no_vencidos = 0
planes_candidatos = 0

for plan in planes:
    print(f"\n🔹 Plan {plan.id}: {plan.nombre}")
    print(f"   Código: {plan.codigo_plan}")
    print(f"   Estado: {plan.estado}")
    print(f"   Gen. Automática: {plan.generacion_automatica}")
    print(f"   Próxima Ejecución: {plan.proxima_ejecucion}")
    print(f"   Activo ID: {plan.activo_id}")

    # Contador de estadísticas
    if plan.estado == "Activo":
        planes_activos += 1
    else:
        planes_inactivos += 1

    if plan.generacion_automatica:
        planes_con_auto += 1
    else:
        planes_sin_auto += 1

    if plan.proxima_ejecucion and plan.proxima_ejecucion <= fecha_objetivo:
        planes_vencidos += 1
        print(f"   ⏰ VENCIDO (próxima ejecución <= mañana)")
    else:
        planes_no_vencidos += 1
        print(f"   ✅ NO VENCIDO (próxima ejecución > mañana)")

    # Verificar si es candidato para generación manual
    es_candidato = (
        plan.estado == "Activo"
        and plan.generacion_automatica == False
        and plan.proxima_ejecucion
        and plan.proxima_ejecucion <= fecha_objetivo
    )

    if es_candidato:
        planes_candidatos += 1
        print(f"   🎯 ES CANDIDATO para generación manual")

        # Verificar si ya tiene orden pendiente
        orden_existente = OrdenTrabajo.query.filter(
            OrdenTrabajo.tipo == "Mantenimiento Preventivo",
            OrdenTrabajo.activo_id == plan.activo_id,
            OrdenTrabajo.descripcion.contains(f"Plan: {plan.codigo_plan}"),
            OrdenTrabajo.estado.in_(["Pendiente", "En Proceso"]),
        ).first()

        if orden_existente:
            print(f"   ⚠️  Ya tiene orden pendiente: {orden_existente.numero_orden}")
        else:
            print(f"   ✅ No tiene orden pendiente")
    else:
        print(f"   ❌ NO es candidato para generación manual")
        if plan.estado != "Activo":
            print(f"      - Razón: Estado no es Activo ({plan.estado})")
        if plan.generacion_automatica:
            print(f"      - Razón: Tiene generación automática activada")
        if not plan.proxima_ejecucion or plan.proxima_ejecucion > fecha_objetivo:
            print(f"      - Razón: Próxima ejecución no está vencida")

print("\n" + "=" * 70)
print("RESUMEN")
print("=" * 70)
print(f"📊 Total de planes: {len(planes)}")
print(f"   ✅ Activos: {planes_activos}")
print(f"   ❌ Inactivos: {planes_inactivos}")
print(f"")
print(f"   🤖 Con generación automática: {planes_con_auto}")
print(f"   👤 Sin generación automática: {planes_sin_auto}")
print(f"")
print(f"   ⏰ Vencidos (próxima ≤ mañana): {planes_vencidos}")
print(f"   📅 No vencidos: {planes_no_vencidos}")
print(f"")
print(f"🎯 CANDIDATOS para generación manual: {planes_candidatos}")

if planes_candidatos == 0:
    print("\n" + "=" * 70)
    print("⚠️  CONCLUSIÓN: NO HAY PLANES CANDIDATOS PARA GENERAR ÓRDENES")
    print("=" * 70)
    print("\nPara que un plan sea candidato debe cumplir:")
    print("  1. Estado = 'Activo'")
    print("  2. generacion_automatica = False")
    print("  3. proxima_ejecucion <= fecha_objetivo (mañana)")
    print("\nSUGERENCIAS:")
    if planes_sin_auto == 0:
        print("  • Desactiva la generación automática en algún plan")
    if planes_vencidos == 0:
        print(
            "  • Ajusta la 'próxima_ejecucion' de algún plan a una fecha pasada o de hoy"
        )
    if planes_activos == 0:
        print("  • Activa al menos un plan de mantenimiento")
else:
    print(f"\n✅ Hay {planes_candidatos} plan(es) listo(s) para generar órdenes")
    print("\n💡 Puedes ejecutar la generación manual desde el botón en la interfaz")

print("=" * 70)
