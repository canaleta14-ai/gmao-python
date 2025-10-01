"""
Script para completar la orden OT-000003 y poder probar
la generación automática con asignación de técnicos.
"""

from app import create_app
from app.extensions import db
from app.models.orden_trabajo import OrdenTrabajo
from datetime import datetime


def completar_orden():
    """Completa la orden OT-000003 para liberar el plan."""
    app = create_app()

    with app.app_context():
        # Buscar la orden OT-000003
        orden = OrdenTrabajo.query.filter_by(numero_orden="OT-000003").first()

        if not orden:
            print("❌ No se encontró la orden OT-000003")
            return

        print(f"\n📋 Orden encontrada: {orden.numero_orden}")
        print(f"   Estado actual: {orden.estado}")
        print(f"   Técnico: {orden.tecnico.nombre if orden.tecnico else 'Sin asignar'}")

        # Cambiar estado a completada
        orden.estado = "Completada"
        orden.fecha_completada = datetime.now()

        # Si no tiene técnico, asignar uno (el que existe)
        if not orden.tecnico_id:
            from app.models.usuario import Usuario

            tecnico = Usuario.query.filter_by(rol="Técnico", activo=True).first()
            if tecnico:
                orden.tecnico_id = tecnico.id
                print(f"   ✅ Técnico asignado: {tecnico.nombre}")

        db.session.commit()

        print(f"   ✅ Orden completada exitosamente")
        print(f"   Fecha completada: {orden.fecha_completada}")
        print("\n✅ Ahora puedes ejecutar: python scheduler_simple.py --test")
        print("   para generar una nueva orden con asignación automática de técnico\n")


if __name__ == "__main__":
    completar_orden()
