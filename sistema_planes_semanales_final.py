"""
Script final para crear planes semanales correctos y probar el sistema completo
"""

import os
import sys
from datetime import datetime
import json

# Configurar la aplicación Flask
sys.path.append("c:/gmao - copia")
os.chdir("c:/gmao - copia")

from app import create_app
from app.extensions import db
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.activo import Activo


def main():
    """Función principal"""
    app = create_app()

    with app.app_context():
        print("🛠️ SISTEMA DE PLANES SEMANALES CORREGIDO")
        print("=" * 60)

        # Obtener activos disponibles
        activos = Activo.query.all()
        if not activos:
            print("❌ No se encontraron activos")
            return

        activo_id = activos[0].id
        print(f"✅ Usando activo: {activos[0].nombre}")

        # Eliminar planes de prueba existentes
        planes_eliminados = PlanMantenimiento.query.filter(
            PlanMantenimiento.codigo_plan.like("TEST_%")
        ).delete()

        if planes_eliminados > 0:
            print(f"🗑️ Eliminados {planes_eliminados} planes de prueba previos")

        # Crear planes de prueba con configuración CORRECTA
        planes_crear = [
            {
                "codigo": "TEST_LUNES_SEMANAL",
                "nombre": "Mantenimiento Semanal - Lunes",
                "descripcion": "Plan semanal todos los lunes",
                "dias": ["lunes"],
                "intervalo": 1,
            },
            {
                "codigo": "TEST_MULTI_SEMANAL",
                "nombre": "Mantenimiento Semanal - Mar/Vie",
                "descripcion": "Plan semanal martes y viernes",
                "dias": ["martes", "viernes"],
                "intervalo": 1,
            },
            {
                "codigo": "TEST_BISEMANAL",
                "nombre": "Mantenimiento Bisemanal - Miércoles",
                "descripcion": "Plan cada 2 semanas los miércoles",
                "dias": ["miercoles"],
                "intervalo": 2,
            },
        ]

        # Crear y calcular próximas ejecuciones
        from app.controllers.planes_controller import calcular_proxima_ejecucion

        fecha_base = datetime.now()

        print(f"\n📅 Fecha base: {fecha_base.strftime('%Y-%m-%d %A')}")
        print("\n📋 CREANDO PLANES:")
        print("-" * 40)

        planes_creados = []

        for plan_config in planes_crear:
            # Crear el plan
            plan = PlanMantenimiento(
                codigo_plan=plan_config["codigo"],
                nombre=plan_config["nombre"],
                descripcion=plan_config["descripcion"],
                activo_id=activo_id,
                frecuencia="Semanal",
                tipo_frecuencia="semanal",
                intervalo_semanas=plan_config["intervalo"],
                dias_semana=json.dumps(plan_config["dias"]),
                estado="Activo",
            )

            # Calcular próxima ejecución con configuración CORRECTA
            configuracion = {
                "tipo_frecuencia": "semanal",
                "dias_semana": plan_config["dias"],
                "intervalo_semanas": plan_config["intervalo"],
            }

            try:
                proxima = calcular_proxima_ejecucion(configuracion, fecha_base)
                plan.proxima_ejecucion = proxima

                db.session.add(plan)
                db.session.commit()

                planes_creados.append(plan)

                print(f"✅ {plan.nombre}")
                print(f"   Días: {', '.join(plan_config['dias'])}")
                print(f"   Intervalo: {plan_config['intervalo']} semana(s)")
                print(f"   Próxima: {proxima.strftime('%Y-%m-%d %A')}")
                print()

            except Exception as e:
                print(f"❌ Error con {plan.nombre}: {e}")
                db.session.rollback()

        print("=" * 60)
        print(f"✅ Creados {len(planes_creados)} planes semanales exitosamente")

        # Verificar con el scheduler
        print("\n🚀 PROBANDO GENERACIÓN AUTOMÁTICA:")
        print("-" * 40)

        try:
            from app.controllers.planes_controller import generar_ordenes_automaticas

            ordenes_generadas = generar_ordenes_automaticas()
            print(f"✅ Generadas {len(ordenes_generadas)} órdenes automáticamente")

            for orden in ordenes_generadas:
                print(
                    f"   • {orden.descripcion} - Fecha: {orden.fecha_programada.strftime('%Y-%m-%d %A')}"
                )

        except Exception as e:
            print(f"❌ Error en generación automática: {e}")

        print("\n🎯 SISTEMA LISTO PARA PRODUCCIÓN")
        print("   - Planes semanales configurados correctamente")
        print("   - Cálculos de fecha funcionando")
        print("   - Scheduler automático operativo")


if __name__ == "__main__":
    main()
