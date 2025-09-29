#!/usr/bin/env python3
"""
Verificar configuración de hora del scheduler
"""
import sys
import os
from datetime import datetime, time as dt_time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def verificar_scheduler_simple():
    """Verificar configuración del scheduler simple"""
    print("🔍 VERIFICANDO CONFIGURACIÓN DEL SCHEDULER")
    print("=" * 50)

    # Importar scheduler
    from scheduler_simple import OrdenesScheduler

    scheduler = OrdenesScheduler()

    print(f"📋 Scheduler Simple:")
    print(f"   • Hora configurada: {scheduler.target_time.strftime('%H:%M')}")
    print(f"   • Esperado: 06:00")

    if scheduler.target_time == dt_time(6, 0):
        print("   ✅ Configuración correcta - 6:00 AM")
        return True
    else:
        print(
            f"   ❌ Configuración incorrecta - {scheduler.target_time.strftime('%H:%M')}"
        )
        return False


def verificar_proxima_ejecucion():
    """Verificar cálculo de próxima ejecución"""
    from scheduler_simple import OrdenesScheduler

    scheduler = OrdenesScheduler()
    proxima = scheduler.calcular_proxima_ejecucion()

    print(f"\n🕐 Próxima Ejecución:")
    print(f"   • Fecha y hora: {proxima.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   • Hora: {proxima.strftime('%H:%M')}")

    if proxima.hour == 6 and proxima.minute == 0:
        print("   ✅ Próxima ejecución a las 6:00 AM")
        return True
    else:
        print(f"   ❌ Hora incorrecta: {proxima.strftime('%H:%M')}")
        return False


if __name__ == "__main__":
    print(f"🕰️ Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    resultado1 = verificar_scheduler_simple()
    resultado2 = verificar_proxima_ejecucion()

    print("\n" + "=" * 50)

    if resultado1 and resultado2:
        print("🎉 ¡CONFIGURACIÓN ACTUALIZADA CORRECTAMENTE!")
        print("✅ El scheduler ahora ejecuta a las 6:00 AM")
        sys.exit(0)
    else:
        print("❌ Hay problemas con la configuración")
        sys.exit(1)
