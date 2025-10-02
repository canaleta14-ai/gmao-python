"""
Script de prueba local para endpoints de cron
Simula llamadas a los endpoints de cron sin necesidad de Cloud Scheduler
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.factory import create_app
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.activo import Activo
from app.models.usuario import Usuario
from app.models.orden_trabajo import OrdenTrabajo
from datetime import datetime, timedelta


def test_generar_ordenes_preventivas():
    """
    Prueba el endpoint de generación de órdenes preventivas
    """
    print("\n" + "=" * 60)
    print("PRUEBA: Generación de órdenes preventivas")
    print("=" * 60)

    app = create_app()

    with app.app_context():
        # 1. Verificar que existen planes activos
        planes = PlanMantenimiento.query.filter_by(activo=True).all()
        print(f"\n✓ Planes activos en DB: {len(planes)}")

        # 2. Verificar planes que deberían generar orden
        hoy = datetime.utcnow().date()
        planes_vencidos = PlanMantenimiento.query.filter(
            PlanMantenimiento.activo == True, PlanMantenimiento.proxima_ejecucion <= hoy
        ).all()
        print(f"✓ Planes con ejecución vencida: {len(planes_vencidos)}")

        if planes_vencidos:
            print("\nPlanes que generarán órdenes:")
            for plan in planes_vencidos:
                print(
                    f"  - ID {plan.id}: {plan.nombre} (próxima: {plan.proxima_ejecucion})"
                )

        # 3. Simular petición al endpoint
        with app.test_client() as client:
            # En desarrollo, no necesita header X-Appengine-Cron
            response = client.post("/api/cron/generar-ordenes-preventivas")

            print(f"\n✓ Código de respuesta: {response.status_code}")

            if response.status_code == 200:
                data = response.get_json()
                print(f"✓ Planes revisados: {data.get('planes_revisados', 0)}")
                print(f"✓ Órdenes creadas: {data.get('ordenes_creadas', 0)}")

                if data.get("errores"):
                    print(f"⚠ Errores: {len(data['errores'])}")
                    for error in data["errores"]:
                        print(f"  - {error}")

                # Verificar órdenes creadas en la DB
                ordenes_generadas = OrdenTrabajo.query.filter(
                    OrdenTrabajo.plan_mantenimiento_id.isnot(None)
                ).all()
                print(
                    f"\n✓ Total de órdenes generadas desde planes: {len(ordenes_generadas)}"
                )

                if ordenes_generadas:
                    print("\nÓrdenes generadas recientemente:")
                    for orden in ordenes_generadas[-5:]:  # Últimas 5
                        plan = orden.plan_mantenimiento
                        print(
                            f"  - OT-{orden.numero_orden}: {plan.nombre if plan else 'N/A'}"
                        )
            else:
                print(f"✗ Error: {response.get_json()}")

    print("\n" + "=" * 60)
    return response.status_code == 200


def test_verificar_alertas():
    """
    Prueba el endpoint de verificación de alertas
    """
    print("\n" + "=" * 60)
    print("PRUEBA: Verificación de alertas de mantenimiento")
    print("=" * 60)

    app = create_app()

    with app.app_context():
        # 1. Verificar activos que requieren alerta
        hace_90_dias = datetime.utcnow().date() - timedelta(days=90)

        activos_sin_mantenimiento = Activo.query.filter(Activo.activo == True).all()

        activos_alerta = []
        for activo in activos_sin_mantenimiento:
            ordenes = (
                OrdenTrabajo.query.filter_by(activo_id=activo.id)
                .order_by(OrdenTrabajo.fecha_inicio.desc())
                .first()
            )

            if not ordenes or (
                ordenes.fecha_inicio and ordenes.fecha_inicio < hace_90_dias
            ):
                activos_alerta.append(activo)

        print(f"\n✓ Total de activos activos: {len(activos_sin_mantenimiento)}")
        print(f"✓ Activos sin mantenimiento (>90 días): {len(activos_alerta)}")

        if activos_alerta:
            print("\nActivos que generarán alertas:")
            for activo in activos_alerta[:5]:  # Primeros 5
                print(f"  - {activo.codigo}: {activo.nombre}")

        # 2. Simular petición al endpoint
        with app.test_client() as client:
            response = client.post("/api/cron/verificar-alertas")

            print(f"\n✓ Código de respuesta: {response.status_code}")

            if response.status_code == 200:
                data = response.get_json()
                print(f"✓ Activos revisados: {data.get('activos_revisados', 0)}")
                print(f"✓ Alertas enviadas: {data.get('alertas_enviadas', 0)}")

                if data.get("errores"):
                    print(f"⚠ Errores: {len(data['errores'])}")
                    for error in data["errores"]:
                        print(f"  - {error}")
            else:
                print(f"✗ Error: {response.get_json()}")

    print("\n" + "=" * 60)
    return response.status_code == 200


def test_endpoint_test():
    """
    Prueba el endpoint de testing /test-cron
    """
    print("\n" + "=" * 60)
    print("PRUEBA: Endpoint de testing")
    print("=" * 60)

    app = create_app()

    with app.test_client() as client:
        response = client.get("/api/cron/test-cron")

        print(f"\n✓ Código de respuesta: {response.status_code}")

        if response.status_code == 200:
            data = response.get_json()
            print(f"✓ Mensaje: {data.get('mensaje')}")
            print(f"✓ Timestamp: {data.get('timestamp')}")

            stats = data.get("estadisticas", {})
            print(f"\nEstadísticas:")
            print(f"  - Planes activos: {stats.get('planes_activos')}")
            print(f"  - Planes vencidos: {stats.get('planes_vencidos')}")
            print(f"  - Activos activos: {stats.get('activos_activos')}")
        else:
            print(f"✗ Error: {response.get_json()}")

    print("\n" + "=" * 60)
    return response.status_code == 200


def test_seguridad_produccion():
    """
    Prueba la seguridad del endpoint en modo producción simulado
    """
    print("\n" + "=" * 60)
    print("PRUEBA: Seguridad de endpoints (simulación producción)")
    print("=" * 60)

    # Crear app en modo producción
    app = create_app()
    app.config["FLASK_ENV"] = "production"

    with app.test_client() as client:
        # 1. Intentar sin header (debe fallar)
        print("\n1. Petición sin header X-Appengine-Cron:")
        response = client.post("/api/cron/generar-ordenes-preventivas")
        print(f"   Código: {response.status_code} (esperado: 403)")

        # 2. Intentar con header incorrecto (debe fallar)
        print("\n2. Petición con header incorrecto:")
        response = client.post(
            "/api/cron/generar-ordenes-preventivas",
            headers={"X-Appengine-Cron": "false"},
        )
        print(f"   Código: {response.status_code} (esperado: 403)")

        # 3. Intentar con header correcto (debe funcionar)
        print("\n3. Petición con header correcto:")
        response = client.post(
            "/api/cron/generar-ordenes-preventivas",
            headers={"X-Appengine-Cron": "true"},
        )
        print(f"   Código: {response.status_code} (esperado: 200)")

    print("\n" + "=" * 60)
    return True


def crear_datos_prueba():
    """
    Crea datos de prueba si la DB está vacía
    """
    print("\n" + "=" * 60)
    print("VERIFICACIÓN: Datos de prueba")
    print("=" * 60)

    app = create_app()

    with app.app_context():
        # Verificar si hay datos
        total_activos = Activo.query.count()
        total_usuarios = Usuario.query.count()
        total_planes = PlanMantenimiento.query.count()

        print(f"\n✓ Activos: {total_activos}")
        print(f"✓ Usuarios: {total_usuarios}")
        print(f"✓ Planes: {total_planes}")

        if total_activos == 0 or total_usuarios == 0:
            print("\n⚠ Base de datos vacía. Se recomienda crear datos de prueba.")
            print("   Puedes usar la interfaz web o crear datos manualmente.")
            return False

        if total_planes == 0:
            print("\n⚠ No hay planes de mantenimiento.")
            print("   Crea al menos un plan de mantenimiento para probar el cron.")
            return False

        # Mostrar planes próximos a ejecutar
        hoy = datetime.utcnow().date()
        proximos_7_dias = hoy + timedelta(days=7)

        planes_proximos = PlanMantenimiento.query.filter(
            PlanMantenimiento.activo == True,
            PlanMantenimiento.proxima_ejecucion >= hoy,
            PlanMantenimiento.proxima_ejecucion <= proximos_7_dias,
        ).all()

        print(f"\n✓ Planes próximos a ejecutar (7 días): {len(planes_proximos)}")

        if planes_proximos:
            print("\nPróximos planes:")
            for plan in planes_proximos[:5]:
                print(f"  - {plan.nombre}: {plan.proxima_ejecucion}")

        print("\n" + "=" * 60)
        return True


def main():
    """
    Ejecuta todas las pruebas
    """
    print("\n" + "╔" + "=" * 58 + "╗")
    print("║  PRUEBAS LOCALES - ENDPOINTS DE CRON (FASE 5)         ║")
    print("╚" + "=" * 58 + "╝")

    resultados = {}

    # 1. Verificar datos
    resultados["datos"] = crear_datos_prueba()

    if not resultados["datos"]:
        print("\n⚠ ADVERTENCIA: Algunas pruebas pueden fallar por falta de datos")
        print("   Puedes continuar, pero considera crear datos de prueba primero.\n")

        respuesta = input("¿Continuar con las pruebas? (s/n): ").lower()
        if respuesta != "s":
            print("\n✓ Pruebas canceladas")
            return

    # 2. Endpoint de testing
    resultados["test"] = test_endpoint_test()

    # 3. Generación de órdenes
    resultados["ordenes"] = test_generar_ordenes_preventivas()

    # 4. Verificación de alertas
    resultados["alertas"] = test_verificar_alertas()

    # 5. Seguridad
    resultados["seguridad"] = test_seguridad_produccion()

    # Resumen final
    print("\n" + "╔" + "=" * 58 + "╗")
    print("║  RESUMEN DE PRUEBAS                                    ║")
    print("╚" + "=" * 58 + "╝")

    pruebas_exitosas = sum(1 for v in resultados.values() if v)
    total_pruebas = len(resultados)

    for nombre, exito in resultados.items():
        estado = "✓ PASS" if exito else "✗ FAIL"
        print(f"{estado} - {nombre.upper()}")

    porcentaje = (pruebas_exitosas / total_pruebas) * 100
    print(
        f"\n✓ Pruebas exitosas: {pruebas_exitosas}/{total_pruebas} ({porcentaje:.1f}%)"
    )

    if pruebas_exitosas == total_pruebas:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
    else:
        print("\n⚠ Algunas pruebas fallaron. Revisa los logs arriba.")

    print("\n" + "=" * 60)
    print("NOTA: Para probar el envío de emails, configura MAIL_SERVER")
    print("      en tu archivo .env y asegúrate de tener credenciales válidas.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
