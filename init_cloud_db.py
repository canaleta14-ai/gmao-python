#!/usr/bin/env python3
"""
Script para inicializar la base de datos de producción directamente
"""
import sys
import os
import logging
import time
import traceback

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Configurar el entorno para producción
    os.environ["FLASK_ENV"] = "production"
    os.environ["SECRET_KEY"] = (
        "c5a07c63d5f7ce831788b3a397e1ebec25703ae38e746177d548d858c6940aca"
    )
    os.environ["DATABASE_URL"] = (
        "postgresql+psycopg2://gmao-user:admin123@"
        "/postgres?host=/cloudsql/mantenimiento-470311:europe-southwest1:gmao-postgres-spain"
    )

    from app.factory import create_app
    from app.extensions import db
    from app.models.usuario import Usuario
    from werkzeug.security import generate_password_hash

    logger.info("=== INICIANDO INICIALIZACIÓN DE BASE DE DATOS ===")

    # Crear aplicación
    app = create_app()

    with app.app_context():
        logger.info("Conectando a la base de datos...")

        # Verificar conexión
        try:
            result = db.session.execute(db.text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"✅ Conectado a PostgreSQL: {version}")
        except Exception as e:
            logger.error(f"❌ Error conectando a la base de datos: {e}")
            sys.exit(1)

        # Crear todas las tablas
        logger.info("Creando todas las tablas...")
        try:
            db.create_all()
            logger.info("✅ Tablas creadas exitosamente")
        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")
            traceback.print_exc()
            sys.exit(1)

        # Verificar si ya existe el usuario admin
        admin_user = Usuario.query.filter_by(username="admin").first()

        if not admin_user:
            logger.info("Creando usuario administrador...")
            try:
                admin_user = Usuario(
                    username="admin",
                    email="admin@mantenimiento.com",
                    nombre="Administrador",
                    apellidos="Sistema",
                    password_hash=generate_password_hash("admin123"),
                    rol="admin",
                    activo=True,
                )
                db.session.add(admin_user)
                db.session.commit()
                logger.info("✅ Usuario admin creado exitosamente")
            except Exception as e:
                logger.error(f"❌ Error creando usuario admin: {e}")
                traceback.print_exc()
                db.session.rollback()
                sys.exit(1)
        else:
            logger.info("✅ Usuario admin ya existe")

        # Verificar tablas creadas
        logger.info("Verificando tablas creadas...")
        try:
            tables_result = db.session.execute(
                db.text(
                    """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
                )
            )
            tables = [row[0] for row in tables_result.fetchall()]
            logger.info(f"✅ Tablas encontradas: {', '.join(tables)}")

            # Verificar usuarios
            users_result = db.session.execute(db.text("SELECT COUNT(*) FROM usuario"))
            user_count = users_result.fetchone()[0]
            logger.info(f"✅ Usuarios en la base de datos: {user_count}")

        except Exception as e:
            logger.error(f"❌ Error verificando tablas: {e}")
            traceback.print_exc()
            sys.exit(1)

        logger.info("=== INICIALIZACIÓN COMPLETADA EXITOSAMENTE ===")
        logger.info("Puedes hacer login con:")
        logger.info("  Usuario: admin")
        logger.info("  Contraseña: admin123")

except Exception as e:
    logger.error(f"❌ Error general: {e}")
    traceback.print_exc()
    sys.exit(1)
