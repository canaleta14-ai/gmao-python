"""
Scheduler para generación automática de órdenes de mantenimiento preventivo
Ejecuta todos los días a las 6:00 AM para generar órdenes del día siguiente
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
from app import create_app
from app.controllers.planes_controller import generar_ordenes_automaticas

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/scheduler_ordenes.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def ejecutar_generacion_ordenes():
    """Ejecutar generación de órdenes con manejo de errores"""
    try:
        app = create_app()
        with app.app_context():
            logger.info("🕚 Iniciando generación programada de órdenes (6:00 AM)")

            resultado = generar_ordenes_automaticas()

            if resultado["success"]:
                ordenes_generadas = resultado.get("ordenes_generadas", 0)
                planes_procesados = resultado.get("planes_procesados", 0)

                logger.info(f"✅ Generación completada exitosamente")
                logger.info(
                    f"📊 Estadísticas: {ordenes_generadas} órdenes generadas de {planes_procesados} planes procesados"
                )

                if "detalles" in resultado:
                    for detalle in resultado["detalles"]:
                        logger.info(f"📋 {detalle}")
            else:
                logger.error(
                    f"❌ Error en generación: {resultado.get('error', 'Error desconocido')}"
                )

    except Exception as e:
        logger.error(f"💥 Error crítico en generación programada: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())


def main():
    """Función principal del scheduler"""
    logger.info("🚀 Iniciando scheduler de órdenes de mantenimiento")
    logger.info("⏰ Configurado para ejecutar todos los días a las 6:00 AM")

    # Programar la tarea para las 6:00 AM todos los días
    schedule.every().day.at("06:00").do(ejecutar_generacion_ordenes)

    # Programar verificación adicional cada 4 horas (opcional)
    # schedule.every(4).hours.do(ejecutar_generacion_ordenes)

    logger.info("✅ Scheduler configurado correctamente")
    logger.info("🔄 Esperando próxima ejecución...")

    # Mostrar próxima ejecución programada
    next_run = schedule.next_run()
    if next_run:
        logger.info(f"📅 Próxima ejecución: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Revisar cada minuto
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler detenido por el usuario")
            break
        except Exception as e:
            logger.error(f"💥 Error en el scheduler: {str(e)}")
            time.sleep(60)  # Continuar después de error


if __name__ == "__main__":
    # Crear directorio de logs si no existe
    import os

    os.makedirs("logs", exist_ok=True)

    # Opción para ejecutar inmediatamente (para pruebas)
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "--test":
        logger.info("🧪 Modo de prueba - Ejecutando generación inmediata")
        ejecutar_generacion_ordenes()
    else:
        main()
