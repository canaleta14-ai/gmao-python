"""
Scheduler simple para generación automática de órdenes de mantenimiento
Ejecuta todos los días a las 6:00 AM usando threading
"""

import threading
import time
import logging
import os
import sys
from datetime import datetime, timedelta, time as dt_time


# Configurar logging
def setup_logging():
    """Configurar sistema de logging"""
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/scheduler_ordenes.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


logger = setup_logging()


class OrdenesScheduler:
    """Scheduler personalizado para generación de órdenes"""

    def __init__(self):
        self.running = False
        self.thread = None
        self.target_time = dt_time(6, 0)  # 6:00 AM

    def ejecutar_generacion_ordenes(self):
        """Ejecutar generación de órdenes con manejo de errores"""
        try:
            # Importar dentro del método para evitar problemas de contexto
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from app import create_app
            from app.controllers.planes_controller import generar_ordenes_automaticas

            app = create_app()
            with app.app_context():
                logger.info("🕚 GENERACIÓN AUTOMÁTICA INICIADA (6:00 AM)")
                logger.info(
                    f"📅 Fecha/hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                logger.info("🎯 Generando órdenes para planes vencidos...")

                resultado = generar_ordenes_automaticas()

                if resultado["success"]:
                    ordenes_generadas = resultado.get("ordenes_generadas", 0)
                    planes_procesados = resultado.get("planes_procesados", 0)

                    logger.info("=" * 50)
                    logger.info("✅ GENERACIÓN COMPLETADA EXITOSAMENTE")
                    logger.info(f"📊 Órdenes generadas: {ordenes_generadas}")
                    logger.info(f"📋 Planes procesados: {planes_procesados}")

                    if "detalles" in resultado and resultado["detalles"]:
                        logger.info("📝 DETALLES DE ÓRDENES GENERADAS:")
                        for i, detalle in enumerate(resultado["detalles"], 1):
                            logger.info(f"   {i}. {detalle}")
                    else:
                        logger.info("ℹ️  No había planes vencidos para procesar")

                    logger.info("=" * 50)

                    # Calcular próxima ejecución
                    siguiente = self.calcular_proxima_ejecucion()
                    logger.info(
                        f"⏰ Próxima ejecución programada: {siguiente.strftime('%Y-%m-%d %H:%M:%S')}"
                    )

                else:
                    error_msg = resultado.get("error", "Error desconocido")
                    logger.error(f"❌ ERROR EN GENERACIÓN: {error_msg}")

        except Exception as e:
            logger.error(f"💥 ERROR CRÍTICO en generación programada: {str(e)}")
            import traceback

            logger.error("🔍 Traceback completo:")
            logger.error(traceback.format_exc())

    def calcular_proxima_ejecucion(self):
        """Calcular la próxima fecha de ejecución (mañana a las 6:00)"""
        ahora = datetime.now()
        manana = ahora.date() + timedelta(days=1)
        proxima = datetime.combine(manana, self.target_time)
        return proxima

    def tiempo_hasta_proxima_ejecucion(self):
        """Calcular segundos hasta la próxima ejecución"""
        ahora = datetime.now()
        proxima = self.calcular_proxima_ejecucion()

        # Si ya pasaron las 6:00 AM de hoy, programar para mañana
        hoy_6am = datetime.combine(ahora.date(), self.target_time)

        if ahora.time() < self.target_time:
            # Aún no son las 6:00 AM de hoy
            proxima = hoy_6am

        diferencia = (proxima - ahora).total_seconds()
        return max(diferencia, 60)  # Mínimo 1 minuto

    def run_scheduler(self):
        """Ejecutar el loop principal del scheduler"""
        logger.info("🚀 SCHEDULER DE ÓRDENES INICIADO")
        logger.info(
            f"⏰ Configurado para ejecutar todos los días a las {self.target_time.strftime('%H:%M')}"
        )

        while self.running:
            try:
                segundos_espera = self.tiempo_hasta_proxima_ejecucion()
                proxima = datetime.now() + timedelta(seconds=segundos_espera)

                logger.info(
                    f"⌛ Esperando {segundos_espera/3600:.1f} horas hasta próxima ejecución"
                )
                logger.info(
                    f"📅 Próxima ejecución: {proxima.strftime('%Y-%m-%d %H:%M:%S')}"
                )

                # Esperar con verificaciones cada minuto
                for _ in range(int(segundos_espera)):
                    if not self.running:
                        break
                    time.sleep(1)

                if self.running:
                    self.ejecutar_generacion_ordenes()

            except Exception as e:
                logger.error(f"💥 Error en scheduler loop: {str(e)}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar

    def start(self):
        """Iniciar el scheduler en un hilo separado"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.thread.start()
            logger.info("✅ Scheduler iniciado en hilo separado")
            return True
        return False

    def stop(self):
        """Detener el scheduler"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            logger.info("🛑 Scheduler detenido")
            return True
        return False


def main():
    """Función principal"""
    scheduler = OrdenesScheduler()

    try:
        # Verificar argumentos de línea de comandos
        if len(sys.argv) > 1:
            if sys.argv[1] == "--test":
                logger.info("🧪 MODO DE PRUEBA - Ejecutando generación inmediata")
                scheduler.ejecutar_generacion_ordenes()
                return
            elif sys.argv[1] == "--status":
                proxima = scheduler.calcular_proxima_ejecucion()
                espera = scheduler.tiempo_hasta_proxima_ejecucion()
                logger.info(f"📊 Estado del scheduler:")
                logger.info(
                    f"   Próxima ejecución: {proxima.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                logger.info(f"   Tiempo de espera: {espera/3600:.1f} horas")
                return

        # Iniciar scheduler
        scheduler.start()

        # Mantener el programa corriendo
        logger.info("🔄 Scheduler en ejecución. Presiona Ctrl+C para detener")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("⏹️  Interrupción recibida, deteniendo scheduler...")
        scheduler.stop()
        logger.info("👋 Scheduler detenido correctamente")
    except Exception as e:
        logger.error(f"💥 Error fatal: {str(e)}")
        scheduler.stop()


if __name__ == "__main__":
    print("📖 Scheduler de Órdenes de Mantenimiento")
    print("   Uso:")
    print("     python scheduler_simple.py           # Iniciar scheduler")
    print("     python scheduler_simple.py --test    # Ejecutar una vez")
    print("     python scheduler_simple.py --status  # Ver estado")
    print()

    main()
