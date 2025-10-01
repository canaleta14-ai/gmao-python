"""Script de diagnóstico completo para la generación automática de órdenes"""

from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.orden_trabajo import OrdenTrabajo
from app.extensions import db
from app import create_app
from datetime import datetime, timedelta

# Crear contexto de aplicación
app = create_app()
app.app_context().push()

print("=" * 80)
print("DIAGNÓSTICO: GENERACIÓN AUTOMÁTICA DE ÓRDENES PREVENTIVAS")
print("=" * 80)

# 1. Verificar planes existentes
planes = PlanMantenimiento.query.all()
print(f"\n📋 TOTAL DE PLANES: {len(planes)}")
print("-" * 80)

if len(planes) == 0:
    print("❌ No hay planes de mantenimiento en la base de datos")
    exit(1)

# 2. Analizar planes para generación AUTOMÁTICA
ahora = datetime.now()

print(f"📅 Fecha/Hora actual: {ahora.strftime('%Y-%m-%d %H:%M:%S')}")
print("-" * 80)

planes_activos = 0
planes_inactivos = 0
planes_con_auto = 0
planes_sin_auto = 0
planes_vencidos = 0
planes_no_vencidos = 0
planes_candidatos_auto = 0

print("\n🔍 ANÁLISIS DETALLADO DE PLANES:\n")

for plan in planes:
    print(f"🔹 Plan {plan.id}: {plan.nombre}")
    print(f"   Código: {plan.codigo_plan}")
    print(f"   Estado: {plan.estado}")
    print(f"   Gen. Automática: {plan.generacion_automatica}")
    print(f"   Próxima Ejecución: {plan.proxima_ejecucion}")
    print(f"   Activo ID: {plan.activo_id}")

    # Estadísticas
    if plan.estado == "Activo":
        planes_activos += 1
    else:
        planes_inactivos += 1

    if plan.generacion_automatica:
        planes_con_auto += 1
    else:
        planes_sin_auto += 1

    # Verificar si está vencido (para generación AUTOMÁTICA)
    if plan.proxima_ejecucion and plan.proxima_ejecucion <= ahora:
        planes_vencidos += 1
        print(f"   ⏰ VENCIDO (próxima ejecución <= ahora)")
    else:
        planes_no_vencidos += 1
        print(f"   ✅ NO VENCIDO (próxima ejecución > ahora)")

    # Verificar si es candidato para generación AUTOMÁTICA
    es_candidato_auto = (
        plan.estado == "Activo"
        and plan.generacion_automatica == True
        and plan.proxima_ejecucion
        and plan.proxima_ejecucion <= ahora
    )

    if es_candidato_auto:
        planes_candidatos_auto += 1
        print(f"   🤖 ES CANDIDATO para generación AUTOMÁTICA")

        # Verificar si ya tiene orden pendiente
        orden_existente = OrdenTrabajo.query.filter(
            OrdenTrabajo.tipo == "Mantenimiento Preventivo",
            OrdenTrabajo.activo_id == plan.activo_id,
            OrdenTrabajo.descripcion.contains(f"Plan: {plan.codigo_plan}"),
            OrdenTrabajo.estado.in_(["Pendiente", "En Proceso"]),
        ).first()

        if orden_existente:
            print(f"   ⚠️  Ya tiene orden pendiente: {orden_existente.numero_orden}")
            print(f"       Estado: {orden_existente.estado}")
            print(f"       Fecha creación: {orden_existente.fecha_creacion}")
        else:
            print(f"   ✅ No tiene orden pendiente - GENERARÁ ORDEN NUEVA")
    else:
        print(f"   ❌ NO es candidato para generación AUTOMÁTICA")
        if plan.estado != "Activo":
            print(f"      - Razón: Estado no es Activo ({plan.estado})")
        if not plan.generacion_automatica:
            print(f"      - Razón: Generación automática desactivada")
        if not plan.proxima_ejecucion or plan.proxima_ejecucion > ahora:
            if plan.proxima_ejecucion:
                diff = plan.proxima_ejecucion - ahora
                dias = diff.days
                horas = diff.seconds // 3600
                print(
                    f"      - Razón: Falta {dias} días y {horas} horas para vencimiento"
                )
            else:
                print(f"      - Razón: No tiene fecha de próxima ejecución")

    print()

print("=" * 80)
print("RESUMEN GENERACIÓN AUTOMÁTICA")
print("=" * 80)
print(f"📊 Total de planes: {len(planes)}")
print(f"   ✅ Activos: {planes_activos}")
print(f"   ❌ Inactivos: {planes_inactivos}")
print(f"")
print(f"   🤖 CON generación automática: {planes_con_auto}")
print(f"   👤 SIN generación automática: {planes_sin_auto}")
print(f"")
print(f"   ⏰ Vencidos (próxima <= ahora): {planes_vencidos}")
print(f"   📅 No vencidos (próxima > ahora): {planes_no_vencidos}")
print(f"")
print(f"🎯 CANDIDATOS para generación AUTOMÁTICA: {planes_candidatos_auto}")

if planes_candidatos_auto == 0:
    print("\n" + "=" * 80)
    print("⚠️  CONCLUSIÓN: NO HAY PLANES PARA GENERAR AUTOMÁTICAMENTE")
    print("=" * 80)
    print("\nPara que un plan genere órdenes AUTOMÁTICAMENTE debe cumplir:")
    print("  1. ✅ Estado = 'Activo'")
    print("  2. ✅ generacion_automatica = True")
    print("  3. ✅ proxima_ejecucion <= fecha_actual")
    print("\nSUGERENCIAS:")
    if planes_con_auto == 0:
        print("  • ⚠️  Ningún plan tiene generación automática activada")
        print("     → Edita un plan y marca 'Generación Automática'")
    if planes_vencidos == 0:
        print("  • ⚠️  Ningún plan está vencido")
        print("     → Espera a que llegue la fecha de 'próxima_ejecucion'")
        print("     → O ajusta manualmente la fecha a una pasada (solo para pruebas)")
    if planes_activos == 0:
        print("  • ⚠️  No hay planes activos")
        print("     → Activa al menos un plan de mantenimiento")
else:
    print(
        f"\n✅ Hay {planes_candidatos_auto} plan(es) listo(s) para generar órdenes AUTOMÁTICAMENTE"
    )
    print("\n💡 El scheduler automático (6:00 AM diario) procesará estos planes")
    print("   O ejecuta manualmente: python scheduler_simple.py --test")

print("\n" + "=" * 80)
print("VERIFICACIÓN DEL SCHEDULER")
print("=" * 80)

# Verificar si existe el archivo del scheduler
import os

archivos_scheduler = [
    "scheduler_simple.py",
    "scheduler_apscheduler.py",
    "scheduler_ordenes.py",
]

print("\n📁 Archivos de scheduler encontrados:")
for archivo in archivos_scheduler:
    existe = os.path.exists(archivo)
    print(f"   {'✅' if existe else '❌'} {archivo}")

print("\n🔧 Para ejecutar prueba manual:")
print("   python scheduler_simple.py --test")

print("\n📅 Para configurar ejecución automática (6:00 AM):")
print("   setup_scheduler_windows.bat (como Administrador)")

print("\n📊 Para ver el calendario de órdenes:")
print("   http://localhost:5000/calendario")

print("=" * 80)
