"""
Script para asignar técnicos automáticamente a órdenes sin técnico
Usa el mismo algoritmo de balanceo de carga del sistema
"""

import sys
import os

# Añadir el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.orden_trabajo import OrdenTrabajo
from app.models.usuario import Usuario
from sqlalchemy import func


def asignar_tecnico_equilibrado():
    """
    Asigna un técnico de forma equilibrada basándose en la carga actual
    (mismo algoritmo que usa generar_orden_individual)
    """
    # Obtener todos los técnicos activos
    tecnicos = Usuario.query.filter_by(rol="tecnico", activo=True).all()

    if not tecnicos:
        print("⚠️  No hay técnicos activos en el sistema")
        return None

    # Contar órdenes pendientes por técnico
    carga_tecnicos = {}
    for tecnico in tecnicos:
        ordenes_pendientes = OrdenTrabajo.query.filter(
            OrdenTrabajo.tecnico_id == tecnico.id,
            OrdenTrabajo.estado.in_(["Pendiente", "En Proceso"]),
        ).count()
        carga_tecnicos[tecnico.id] = ordenes_pendientes

    # Asignar al técnico con menos carga
    tecnico_id = min(carga_tecnicos, key=carga_tecnicos.get)
    return tecnico_id


def asignar_tecnicos_masivo():
    """
    Asigna técnicos a todas las órdenes que no tienen técnico asignado
    """
    app = create_app()

    with app.app_context():
        # Buscar todas las órdenes sin técnico
        ordenes_sin_tecnico = OrdenTrabajo.query.filter(
            OrdenTrabajo.tecnico_id == None
        ).all()

        if not ordenes_sin_tecnico:
            print("✅ No hay órdenes sin técnico asignado")
            return

        print(f"\n📋 Encontradas {len(ordenes_sin_tecnico)} órdenes sin técnico")
        print(f"{'='*60}")

        # Contar técnicos disponibles
        tecnicos_activos = Usuario.query.filter_by(rol="tecnico", activo=True).count()

        if tecnicos_activos == 0:
            print("❌ ERROR: No hay técnicos activos en el sistema")
            return

        print(f"👥 Técnicos activos disponibles: {tecnicos_activos}")
        print(f"{'='*60}\n")

        asignadas = 0
        errores = 0

        for orden in ordenes_sin_tecnico:
            try:
                tecnico_id = asignar_tecnico_equilibrado()

                if tecnico_id:
                    orden.tecnico_id = tecnico_id
                    tecnico = Usuario.query.get(tecnico_id)

                    print(
                        f"✓ Orden #{orden.numero_orden} (ID: {orden.id}) → {tecnico.nombre}"
                    )
                    asignadas += 1
                else:
                    print(
                        f"⚠️  Orden #{orden.numero_orden} (ID: {orden.id}) → No se pudo asignar técnico"
                    )
                    errores += 1

            except Exception as e:
                print(f"❌ Error en orden #{orden.numero_orden}: {str(e)}")
                errores += 1

        # Guardar cambios
        try:
            db.session.commit()
            print(f"\n{'='*60}")
            print(f"✅ COMPLETADO: {asignadas} órdenes asignadas exitosamente")
            if errores > 0:
                print(f"⚠️  {errores} órdenes con errores")
            print(f"{'='*60}\n")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR al guardar cambios: {str(e)}")
            print("Se revirtieron todos los cambios\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔧 ASIGNACIÓN MASIVA DE TÉCNICOS A ÓRDENES")
    print("=" * 60)

    asignar_tecnicos_masivo()
