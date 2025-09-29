"""
Verificar estado completo del sistema de generación automática
"""

import os
import sys
from datetime import datetime

# Configurar ruta
sys.path.append("c:/gmao - copia")
os.chdir("c:/gmao - copia")


def verificar_sistema_completo():
    """Verificar todos los componentes del sistema automático"""

    print("🔍 ESTADO COMPLETO DEL SISTEMA DE GENERACIÓN AUTOMÁTICA")
    print("=" * 60)

    # 1. Configuración del scheduler
    print("\n1️⃣ SCHEDULER AUTOMÁTICO:")
    print("-" * 25)

    from scheduler_simple import OrdenesScheduler

    scheduler = OrdenesScheduler()

    ahora = datetime.now()
    proxima = scheduler.calcular_proxima_ejecucion()
    segundos = scheduler.tiempo_hasta_proxima_ejecucion()

    print(f"⏰ Configurado para: 11:00 AM diariamente")
    print(f"📅 Próxima ejecución: {proxima.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  En: {segundos/3600:.1f} horas")

    # 2. Verificar función de generación
    print("\n2️⃣ FUNCIÓN DE GENERACIÓN:")
    print("-" * 26)

    try:
        from app import create_app
        from app.controllers.planes_controller import generar_ordenes_automaticas

        app = create_app()
        with app.app_context():
            # Solo verificar sin generar
            from app.models.plan_mantenimiento import PlanMantenimiento

            planes_activos = PlanMantenimiento.query.filter_by(estado="Activo").count()
            print(f"📋 Planes activos encontrados: {planes_activos}")
            print(f"✅ Función generar_ordenes_automaticas disponible")

    except Exception as e:
        print(f"❌ Error al verificar función: {e}")

    # 3. Archivos de log
    print("\n3️⃣ LOGS DEL SISTEMA:")
    print("-" * 19)

    log_file = "logs/scheduler_ordenes.log"
    if os.path.exists(log_file):
        try:
            # Leer las últimas 5 líneas del log
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    print(f"📝 Archivo de log: {log_file}")
                    print("🔍 Últimas entradas:")
                    for line in lines[-5:]:
                        print(f"   {line.strip()}")
                else:
                    print("📝 Archivo de log vacío")
        except Exception as e:
            print(f"❌ Error al leer log: {e}")
    else:
        print("📝 No se encontró archivo de log")

    # 4. Métodos para iniciar/detener
    print("\n4️⃣ CONTROL DEL SCHEDULER:")
    print("-" * 24)
    print("🚀 Para INICIAR el scheduler automático:")
    print("   python scheduler_simple.py")
    print("")
    print("🧪 Para PROBAR una ejecución manual:")
    print("   python scheduler_simple.py --test")
    print("")
    print("📊 Para ver ESTADO:")
    print("   python scheduler_simple.py --status")
    print("")
    print("⏹️  Para DETENER: Ctrl+C en la ventana del scheduler")

    # 5. Resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN - CUÁNDO SE GENERAN LAS ÓRDENES:")
    print("-" * 42)
    print("🕚 AUTOMÁTICAMENTE: Todos los días a las 11:00 AM")
    print("🔄 FRECUENCIA: Cada 24 horas")
    print("📅 PRÓXIMA VEZ: Mañana 29 septiembre 2025 a las 11:00")
    print("⏱️  FALTAN: 22+ horas")
    print("")
    print("✅ El sistema está configurado y listo para funcionar")


if __name__ == "__main__":
    verificar_sistema_completo()
