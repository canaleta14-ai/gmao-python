"""
Script simplificado para crear y probar planes semanales
"""

import os
import sys

# Configurar la aplicación Flask
sys.path.append("c:/gmao - copia")
os.chdir("c:/gmao - copia")

from app import create_app
from app.extensions import db
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.activo import Activo
from datetime import datetime
import json


def main():
    """Función principal"""
    app = create_app()

    with app.app_context():
        print("🛠️ CREANDO Y PROBANDO PLANES SEMANALES")
        print("=" * 50)

        # Obtener primer activo disponible
        activos = Activo.query.all()
        if not activos:
            print("❌ No se encontraron activos")
            return

        activo_id = activos[0].id
        print(f"✅ Usando activo: {activos[0].nombre}")

        # Eliminar planes de prueba previos
        PlanMantenimiento.query.filter(
            PlanMantenimiento.codigo_plan.like("TEST_%")
        ).delete()

        # Crear plan de prueba para lunes
        plan_lunes = PlanMantenimiento(
            codigo_plan="TEST_LUNES_001",
            nombre="Test Semanal - Lunes",
            descripcion="Plan de prueba semanal",
            activo_id=activo_id,
            frecuencia="Semanal",
            tipo_frecuencia="semanal",
            intervalo_semanas=1,
            dias_semana=json.dumps(["lunes"]),
            estado="Activo",
        )

        db.session.add(plan_lunes)
        db.session.commit()

        print(f"✅ Plan creado: {plan_lunes.nombre} (ID: {plan_lunes.id})")

        # Probar cálculo
        from app.controllers.planes_controller import calcular_proxima_ejecucion

        fecha_base = datetime.now()
        print(f"📅 Fecha base: {fecha_base.strftime('%Y-%m-%d %A')}")

        configuracion = {
            "tipo": "semanal",
            "dias_semana": ["lunes"],
            "intervalo_semanas": 1,
        }

        try:
            proxima = calcular_proxima_ejecucion(configuracion, fecha_base)
            print(f"✅ Próxima ejecución: {proxima.strftime('%Y-%m-%d %A')}")

            # Actualizar el plan
            plan_lunes.proxima_ejecucion = proxima
            db.session.commit()
            print("✅ Plan actualizado con próxima ejecución")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    main()
