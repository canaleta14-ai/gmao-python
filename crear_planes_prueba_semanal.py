"""
Script para crear planes de prueba y validar el cálculo semanal corregido
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


def crear_planes_prueba():
    """Crear planes de prueba para validar el cálculo semanal"""
    app = create_app()

    with app.app_context():
        print("🛠️ CREANDO PLANES DE PRUEBA SEMANAL")
        print("=" * 50)

        # Verificar si hay activos disponibles
        activos = Activo.query.all()
        if not activos:
            print("❌ No se encontraron activos. Creando activo de prueba...")
            activo_prueba = Activo(
                nombre="Máquina Test Semanal",
                descripcion="Máquina para probar planes semanales",
                ubicacion="Área de pruebas",
            )
            db.session.add(activo_prueba)
            db.session.commit()
            activos = [activo_prueba]

        activo_id = activos[0].id
        print(f"✅ Usando activo ID: {activo_id} ({activos[0].nombre})")

        # Plan 1: Mantenimiento semanal los lunes
        plan_lunes = PlanMantenimiento(
            nombre="Test Semanal - Lunes",
            descripcion="Plan de prueba para validar cálculo semanal - Lunes",
            activo_id=activo_id,
            frecuencia="Semanal",
            configuracion_frecuencia=json.dumps(
                {"tipo": "semanal", "dias_semana": ["lunes"], "intervalo": 1}
            ),
            estado="Activo",
            prioridad="Media",
        )

        # Plan 2: Mantenimiento semanal los martes y jueves
        plan_multi = PlanMantenimiento(
            nombre="Test Semanal - Martes y Jueves",
            descripcion="Plan de prueba para múltiples días",
            activo_id=activo_id,
            frecuencia="Semanal",
            configuracion_frecuencia=json.dumps(
                {"tipo": "semanal", "dias_semana": ["martes", "jueves"], "intervalo": 1}
            ),
            estado="Activo",
            prioridad="Media",
        )

        # Plan 3: Mantenimiento bisemanal los viernes
        plan_bisemanal = PlanMantenimiento(
            nombre="Test Bisemanal - Viernes",
            descripcion="Plan de prueba cada 2 semanas",
            activo_id=activo_id,
            frecuencia="Semanal",
            configuracion_frecuencia=json.dumps(
                {"tipo": "semanal", "dias_semana": ["viernes"], "intervalo": 2}
            ),
            estado="Activo",
            prioridad="Media",
        )

        # Eliminar planes previos de prueba
        planes_existentes = PlanMantenimiento.query.filter(
            PlanMantenimiento.nombre.like("Test %")
        ).all()

        for plan in planes_existentes:
            db.session.delete(plan)

        # Añadir nuevos planes
        db.session.add(plan_lunes)
        db.session.add(plan_multi)
        db.session.add(plan_bisemanal)
        db.session.commit()

        print(f"✅ Plan creado: {plan_lunes.nombre} (ID: {plan_lunes.id})")
        print(f"✅ Plan creado: {plan_multi.nombre} (ID: {plan_multi.id})")
        print(f"✅ Plan creado: {plan_bisemanal.nombre} (ID: {plan_bisemanal.id})")

        return [plan_lunes, plan_multi, plan_bisemanal]


def probar_calculos():
    """Probar los cálculos de próxima ejecución"""
    from app.controllers.planes_controller import calcular_proxima_ejecucion

    app = create_app()
    with app.app_context():
        print("\n🧪 PROBANDO CÁLCULOS DE FECHA")
        print("=" * 50)

        # Obtener planes de prueba
        planes_test = PlanMantenimiento.query.filter(
            PlanMantenimiento.nombre.like("Test %")
        ).all()

        fecha_base = datetime.now()
        print(f"📅 Fecha base: {fecha_base.strftime('%Y-%m-%d %A')}")
        print()

        for plan in planes_test:
            print(f"📋 Plan: {plan.nombre}")
            configuracion = json.loads(plan.configuracion_frecuencia or "{}")
            print(f"   Configuración: {configuracion}")

            try:
                proxima = calcular_proxima_ejecucion(configuracion, fecha_base)
                print(f"   ✅ Próxima ejecución: {proxima.strftime('%Y-%m-%d %A')}")
            except Exception as e:
                print(f"   ❌ Error: {e}")

            print()


def main():
    """Función principal"""
    try:
        # Crear planes de prueba
        planes = crear_planes_prueba()

        # Probar cálculos
        probar_calculos()

        print("✅ Pruebas completadas exitosamente")

    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
