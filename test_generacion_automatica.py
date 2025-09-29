#!/usr/bin/env python3
"""
Prueba del campo generacion_automatica en planes de mantenimiento
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.activo import Activo
from app.extensions import db


def test_generacion_automatica():
    """Prueba el campo generacion_automatica en planes"""

    app = create_app()

    with app.app_context():
        print("\n🧪 PRUEBA DEL CAMPO GENERACIÓN AUTOMÁTICA")
        print("=" * 50)

        # 1. Verificar que el campo existe en la base de datos
        print("1. Verificando esquema de la base de datos...")
        with db.engine.connect() as connection:
            result = connection.execute(
                db.text("PRAGMA table_info(plan_mantenimiento)")
            )
            columns = result.fetchall()

        generacion_field = None
        for col in columns:
            if col[1] == "generacion_automatica":
                generacion_field = col
                break

        if generacion_field:
            print("✅ Campo 'generacion_automatica' encontrado en la base de datos")
            print(f"   Tipo: {generacion_field[2]}, Default: {generacion_field[4]}")
        else:
            print("❌ Campo 'generacion_automatica' NO encontrado")
            return False

        # 2. Verificar planes existentes
        print("\n2. Verificando planes existentes...")
        planes = PlanMantenimiento.query.all()
        print(f"   Total de planes: {len(planes)}")

        for i, plan in enumerate(planes[:3]):  # Solo mostrar los primeros 3
            print(
                f"   Plan {i+1}: '{plan.codigo_plan}' - Generación automática: {plan.generacion_automatica}"
            )

        # 3. Verificar filtrado para generación automática
        print("\n3. Verificando filtrado de planes...")
        planes_automaticos = PlanMantenimiento.query.filter(
            PlanMantenimiento.generacion_automatica == True
        ).all()
        planes_manuales = PlanMantenimiento.query.filter(
            PlanMantenimiento.generacion_automatica == False
        ).all()

        print(f"   Planes con generación automática: {len(planes_automaticos)}")
        print(f"   Planes con generación manual: {len(planes_manuales)}")

        print("\n🎉 PRUEBA COMPLETADA EXITOSAMENTE")
        return True


if __name__ == "__main__":
    if test_generacion_automatica():
        print("\n✅ TODAS LAS PRUEBAS PASARON")
        sys.exit(0)
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
        sys.exit(1)
