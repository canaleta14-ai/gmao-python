from app import create_app
from app.models.orden_trabajo import OrdenTrabajo
from app.models.plan_mantenimiento import PlanMantenimiento
from app.extensions import db


def limpiar_base_datos():
    """Limpiar órdenes y resetear planes para empezar de cero"""
    app = create_app()

    with app.app_context():
        print("🧹 LIMPIEZA COMPLETA DE BASE DE DATOS")
        print("=" * 50)

        # 1. Contar datos actuales
        ordenes_count = OrdenTrabajo.query.count()
        planes_count = PlanMantenimiento.query.count()

        print(f"📊 Estado actual:")
        print(f"   - Órdenes de trabajo: {ordenes_count}")
        print(f"   - Planes de mantenimiento: {planes_count}")

        # 2. Mostrar órdenes existentes
        if ordenes_count > 0:
            print(f"\n📋 Órdenes existentes:")
            ordenes = OrdenTrabajo.query.all()
            for orden in ordenes:
                fecha_str = (
                    orden.fecha_programada.strftime("%Y-%m-%d %A")
                    if orden.fecha_programada
                    else "Sin fecha"
                )
                print(
                    f"   - {orden.numero_orden}: {fecha_str} - {orden.descripcion[:50]}..."
                )

        # 3. Mostrar planes existentes
        if planes_count > 0:
            print(f"\n📋 Planes existentes:")
            planes = PlanMantenimiento.query.all()
            for plan in planes:
                fecha_str = (
                    plan.proxima_ejecucion.strftime("%Y-%m-%d %A")
                    if plan.proxima_ejecucion
                    else "Sin fecha"
                )
                print(f"   - {plan.codigo_plan}: {plan.tipo_frecuencia} - {fecha_str}")

        # 4. Eliminar todas las órdenes
        print(f"\n🗑️ Eliminando todas las órdenes de trabajo...")
        OrdenTrabajo.query.delete()

        # 5. Eliminar todos los planes
        print(f"🗑️ Eliminando todos los planes de mantenimiento...")
        PlanMantenimiento.query.delete()

        # 6. Commit cambios
        db.session.commit()

        print(f"\n✅ Limpieza completada:")
        print(f"   - {ordenes_count} órdenes eliminadas")
        print(f"   - {planes_count} planes eliminados")
        print(f"   - Base de datos lista para nueva configuración")


if __name__ == "__main__":
    limpiar_base_datos()
