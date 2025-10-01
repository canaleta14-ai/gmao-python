"""
Script de prueba para verificar la asignación equilibrada de técnicos
al generar órdenes de trabajo desde planes de mantenimiento.
"""

from app import create_app
from app.extensions import db
from app.models.usuario import Usuario
from app.models.orden_trabajo import OrdenTrabajo
from app.models.plan_mantenimiento import PlanMantenimiento
from datetime import datetime


def mostrar_estado_actual():
    """Muestra el estado actual de técnicos y sus cargas de trabajo."""
    print("\n" + "=" * 80)
    print("ESTADO ACTUAL DE TÉCNICOS Y CARGAS DE TRABAJO")
    print("=" * 80)

    # Obtener todos los técnicos activos
    tecnicos = Usuario.query.filter(
        Usuario.activo == True, Usuario.rol.in_(["Técnico", "Supervisor"])
    ).all()

    if not tecnicos:
        print("⚠️ No hay técnicos activos en el sistema")
        return

    print(f"\nTotal de técnicos activos: {len(tecnicos)}\n")

    for tecnico in tecnicos:
        # Contar órdenes activas (Pendiente o En Proceso)
        ordenes_activas = OrdenTrabajo.query.filter(
            OrdenTrabajo.tecnico_id == tecnico.id,
            OrdenTrabajo.estado.in_(["Pendiente", "En Proceso"]),
        ).all()

        print(f"👤 {tecnico.nombre} ({tecnico.rol})")
        print(f"   ID: {tecnico.id}")
        print(f"   Órdenes activas: {len(ordenes_activas)}")

        if ordenes_activas:
            print("   Detalles de órdenes:")
            for orden in ordenes_activas:
                print(
                    f"      - {orden.numero_orden}: {orden.descripcion[:50]}... [{orden.estado}]"
                )
        print()

    print("=" * 80)


def mostrar_ordenes_recientes():
    """Muestra las últimas órdenes generadas y sus técnicos asignados."""
    print("\n" + "=" * 80)
    print("ÚLTIMAS 10 ÓRDENES GENERADAS")
    print("=" * 80 + "\n")

    ordenes = (
        OrdenTrabajo.query.order_by(OrdenTrabajo.fecha_creacion.desc()).limit(10).all()
    )

    if not ordenes:
        print("⚠️ No hay órdenes en el sistema")
        return

    for orden in ordenes:
        tecnico_nombre = orden.tecnico.nombre if orden.tecnico else "Sin asignar"
        print(f"📋 {orden.numero_orden}")
        print(f"   Descripción: {orden.descripcion[:60]}...")
        print(f"   Estado: {orden.estado}")
        print(f"   Técnico: {tecnico_nombre}")
        print(f"   Fecha creación: {orden.fecha_creacion}")
        print()

    print("=" * 80)


def mostrar_planes_candidatos():
    """Muestra los planes que pueden generar órdenes automáticamente."""
    print("\n" + "=" * 80)
    print("PLANES CON GENERACIÓN AUTOMÁTICA ACTIVA")
    print("=" * 80 + "\n")

    ahora = datetime.now()

    planes = PlanMantenimiento.query.filter(
        PlanMantenimiento.generacion_automatica == True,
        PlanMantenimiento.estado == "Activo",
        PlanMantenimiento.proxima_ejecucion <= ahora,
    ).all()

    if not planes:
        print("ℹ️ No hay planes listos para generar órdenes automáticamente")
        print(f"   (Hora actual: {ahora.strftime('%Y-%m-%d %H:%M:%S')})")
    else:
        print(f"Total de planes listos: {len(planes)}\n")
        for plan in planes:
            print(f"📅 {plan.codigo_plan} - {plan.nombre}")
            print(f"   Próxima ejecución: {plan.proxima_ejecucion}")
            print(f"   Frecuencia: {plan.frecuencia}")
            if plan.activo:
                print(f"   Activo: {plan.activo.nombre}")
            print()

    print("=" * 80)


def mostrar_estadisticas_asignacion():
    """Muestra estadísticas sobre la distribución de órdenes entre técnicos."""
    print("\n" + "=" * 80)
    print("ESTADÍSTICAS DE DISTRIBUCIÓN DE ÓRDENES")
    print("=" * 80 + "\n")

    tecnicos = Usuario.query.filter(
        Usuario.activo == True, Usuario.rol.in_(["Técnico", "Supervisor"])
    ).all()

    if not tecnicos:
        print("⚠️ No hay técnicos en el sistema")
        return

    total_ordenes = 0
    cargas = []

    for tecnico in tecnicos:
        ordenes_pendientes = OrdenTrabajo.query.filter(
            OrdenTrabajo.tecnico_id == tecnico.id, OrdenTrabajo.estado == "Pendiente"
        ).count()

        ordenes_en_proceso = OrdenTrabajo.query.filter(
            OrdenTrabajo.tecnico_id == tecnico.id, OrdenTrabajo.estado == "En Proceso"
        ).count()

        ordenes_completadas = OrdenTrabajo.query.filter(
            OrdenTrabajo.tecnico_id == tecnico.id, OrdenTrabajo.estado == "Completada"
        ).count()

        total_tecnico = ordenes_pendientes + ordenes_en_proceso + ordenes_completadas
        total_ordenes += total_tecnico

        cargas.append(
            {
                "nombre": tecnico.nombre,
                "pendientes": ordenes_pendientes,
                "en_proceso": ordenes_en_proceso,
                "completadas": ordenes_completadas,
                "total": total_tecnico,
                "activas": ordenes_pendientes + ordenes_en_proceso,
            }
        )

    # Ordenar por carga activa
    cargas.sort(key=lambda x: x["activas"], reverse=True)

    print(f"Total de órdenes en el sistema: {total_ordenes}\n")

    # Tabla de distribución
    print(
        f"{'TÉCNICO':<30} {'PENDIENTES':>12} {'EN PROCESO':>12} {'COMPLETADAS':>12} {'ACTIVAS':>10} {'TOTAL':>10}"
    )
    print("-" * 90)

    for carga in cargas:
        print(
            f"{carga['nombre']:<30} {carga['pendientes']:>12} {carga['en_proceso']:>12} {carga['completadas']:>12} {carga['activas']:>10} {carga['total']:>10}"
        )

    print("-" * 90)

    # Cálculo de equilibrio
    if cargas:
        max_activas = cargas[0]["activas"]
        min_activas = cargas[-1]["activas"]
        diferencia = max_activas - min_activas

        print(f"\nDiferencia entre mayor y menor carga activa: {diferencia} órdenes")

        if diferencia == 0:
            print("✅ La carga está perfectamente equilibrada")
        elif diferencia <= 2:
            print("✅ La carga está bien equilibrada")
        elif diferencia <= 5:
            print("⚠️ La carga tiene un desequilibrio moderado")
        else:
            print("❌ La carga está muy desequilibrada")

    print("\n" + "=" * 80)


def main():
    """Función principal del script."""
    app = create_app()

    with app.app_context():
        print("\n" + "=" * 80)
        print("TEST DE ASIGNACIÓN EQUILIBRADA DE TÉCNICOS")
        print("=" * 80)
        print(f"Fecha/Hora actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Mostrar información actual
        mostrar_estado_actual()
        mostrar_planes_candidatos()
        mostrar_ordenes_recientes()
        mostrar_estadisticas_asignacion()

        print("\n" + "=" * 80)
        print("RESUMEN")
        print("=" * 80)
        print(
            """
Para probar la generación automática de órdenes con asignación equilibrada:

1. Ejecutar generación automática:
   python scheduler_simple.py --test

2. O ejecutar generación manual desde la interfaz web:
   - Navegar a Mantenimiento Preventivo
   - Hacer clic en "Generar órdenes manualmente"

3. Luego ejecutar este script nuevamente para ver los cambios:
   python test_asignacion_equilibrada.py

NOTA: El sistema asignará automáticamente técnicos basándose en su
carga de trabajo actual (órdenes Pendientes + En Proceso).
        """
        )
        print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
