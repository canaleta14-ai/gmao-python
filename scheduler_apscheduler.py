"""
Scheduler usando APScheduler para generación automática de órdenes
Ejecuta todos los días a las 6:00 AM para generar órdenes del día siguiente
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

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
        # Importar dentro de la función para evitar problemas de contexto
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import create_app
        from app.controllers.planes_controller import generar_ordenes_automaticas

        app = create_app()
        with app.app_context():
            logger.info("🕚 Iniciando generación programada de órdenes (6:00 AM)")
            logger.info(
                f"📅 Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            resultado = generar_ordenes_automaticas()

            if resultado["success"]:
                ordenes_generadas = resultado.get("ordenes_generadas", 0)
                planes_procesados = resultado.get("planes_procesados", 0)

                logger.info(f"✅ Generación completada exitosamente")
                logger.info(
                    f"📊 Estadísticas: {ordenes_generadas} órdenes generadas de {planes_procesados} planes procesados"
                )

                if "detalles" in resultado and resultado["detalles"]:
                    logger.info("📋 Detalles de órdenes generadas:")
                    for detalle in resultado["detalles"]:
                        logger.info(f"   • {detalle}")
                else:
                    logger.info(
                        "📋 No se generaron nuevas órdenes (no hay planes vencidos)"
                    )

            else:
                logger.error(
                    f"❌ Error en generación: {resultado.get('error', 'Error desconocido')}"
                )

    except Exception as e:
        logger.error(f"💥 Error crítico en generación programada: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())


def main():
    """Función principal del scheduler con APScheduler"""
    logger.info("🚀 Iniciando APScheduler para órdenes de mantenimiento")
    logger.info("⏰ Configurado para ejecutar todos los días a las 6:00 AM")

    # Crear scheduler
    scheduler = BlockingScheduler()

    # Programar la tarea para las 6:00 AM todos los días
    scheduler.add_job(
        func=ejecutar_generacion_ordenes,
        trigger=CronTrigger(hour=6, minute=0),
        id="generar_ordenes_6am",
        name="Generación de Órdenes Preventivas 6:00 AM",
        replace_existing=True,
    )

    # Opcional: Programar verificación adicional a las 6:00 AM
    # scheduler.add_job(
    #     func=ejecutar_generacion_ordenes,
    #     trigger=CronTrigger(hour=6, minute=0),
    #     id='generar_ordenes_6am',
    #     name='Verificación Temprana 6:00 AM',
    #     replace_existing=True
    # )

    # Configurar cierre limpio
    atexit.register(lambda: scheduler.shutdown())

    logger.info("✅ Scheduler configurado correctamente")

    try:
        # Mostrar próximas ejecuciones
        jobs = scheduler.get_jobs()
        for job in jobs:
            next_run = job.next_run_time
            if next_run:
                logger.info(f"📅 {job.name}: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

        logger.info("🔄 Scheduler iniciado, presiona Ctrl+C para detener")
        scheduler.start()

    except KeyboardInterrupt:
        logger.info("🛑 Scheduler detenido por el usuario")
        scheduler.shutdown()
    except Exception as e:
        logger.error(f"💥 Error en el scheduler: {str(e)}")
        scheduler.shutdown()


if __name__ == "__main__":
    # Crear directorio de logs si no existe
    os.makedirs("logs", exist_ok=True)

    # Opción para ejecutar inmediatamente (para pruebas)
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        logger.info("🧪 Modo de prueba - Ejecutando generación inmediata")
        ejecutar_generacion_ordenes()
    elif len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        main()
    else:
        logger.info("📖 Uso del scheduler:")
        logger.info("  python scheduler_apscheduler.py --schedule  # Iniciar scheduler")
        logger.info("  python scheduler_apscheduler.py --test      # Ejecutar una vez")
        main()  # Iniciar por defecto
