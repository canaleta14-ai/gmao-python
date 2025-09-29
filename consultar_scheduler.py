"""
Consultar estado actual del scheduler
"""

import os
import sys
from datetime import datetime

# Configurar ruta
sys.path.append("c:/gmao - copia")
os.chdir("c:/gmao - copia")

from scheduler_simple import OrdenesScheduler


def consultar_scheduler():
    """Consultar configuración actual"""
    scheduler = OrdenesScheduler()

    print("⏰ CONFIGURACIÓN DEL SCHEDULER DE ÓRDENES")
    print("=" * 45)

    # Hora configurada
    print(f"🕚 Hora programada: {scheduler.target_time.strftime('%H:%M')} (11:00 AM)")

    # Fecha/hora actual
    ahora = datetime.now()
    print(f"📅 Fecha/hora actual: {ahora.strftime('%Y-%m-%d %H:%M:%S')}")

    # Próxima ejecución
    proxima = scheduler.calcular_proxima_ejecucion()
    print(f"⏭️  Próxima ejecución: {proxima.strftime('%Y-%m-%d %H:%M:%S')}")

    # Tiempo restante
    segundos = scheduler.tiempo_hasta_proxima_ejecucion()
    horas = segundos / 3600
    minutos = segundos / 60

    print(f"⏱️  Tiempo restante: {horas:.1f} horas ({minutos:.0f} minutos)")

    # Frecuencia
    print(f"🔄 Frecuencia: Diaria")
    print(f"📝 Descripción: Genera órdenes automáticamente todos los días")

    # Estado del sistema
    print("\n✅ RESUMEN:")
    print("   • El scheduler se ejecuta automáticamente todos los días")
    print("   • Hora exacta: 11:00 AM (cada 24 horas)")
    print("   • Genera órdenes para planes vencidos o próximos a vencer")
    print("   • Funciona en segundo plano")


if __name__ == "__main__":
    consultar_scheduler()
