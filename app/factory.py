from flask import Flask, render_template, request
from app.extensions import db
from flask_login import LoginManager
import logging
import os
from datetime import datetime


def create_app():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    static_dir = os.path.join(base_dir, "static")
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    # Configuración de logging
    if not app.debug:
        # Configuración para producción
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("logs/gmao.log"), logging.StreamHandler()],
        )
        # Crear directorio de logs si no existe
        os.makedirs("logs", exist_ok=True)
    else:
        # Configuración para desarrollo - también loggear a archivo
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("logs/gmao_debug.log"),
                logging.StreamHandler(),
            ],
        )
        # Crear directorio de logs si no existe
        os.makedirs("logs", exist_ok=True)

    # Configuración de SECRET_KEY desde Secret Manager (producción) o .env (desarrollo)
    from app.utils.secrets import get_secret_or_env

    app.config["SECRET_KEY"] = get_secret_or_env(
        secret_id="gmao-secret-key",
        env_var="SECRET_KEY",
        default="dev-secret-key-INSEGURO-CAMBIAR-EN-PRODUCCION",
    )

    # Log de advertencia si se usa clave por defecto
    if app.config["SECRET_KEY"] == "dev-secret-key-INSEGURO-CAMBIAR-EN-PRODUCCION":
        app.logger.warning("⚠️  Usando SECRET_KEY por defecto - NO USAR EN PRODUCCIÓN")
    else:
        app.logger.info("✅ SECRET_KEY configurada correctamente")

    # Configuración de sesión para cerrar al cerrar navegador
    app.config["PERMANENT_SESSION_LIFETIME"] = 86400  # 24 horas
    app.config["SESSION_PERMANENT"] = True  # Mantener sesiones permanentes
    app.config["SESSION_COOKIE_HTTPONLY"] = (
        True  # Solo accesible via HTTP, no JavaScript
    )

    # Activar HTTPS solo en producción
    is_production = (
        os.getenv("GAE_ENV", "").startswith("standard")
        or os.getenv("FLASK_ENV") == "production"
    )
    app.config["SESSION_COOKIE_SECURE"] = is_production
    app.config["REMEMBER_COOKIE_SECURE"] = is_production

    # Log de configuración de seguridad
    if is_production:
        app.logger.info("🔒 Modo producción: Cookies seguras activadas (HTTPS)")
    else:
        app.logger.info("🔓 Modo desarrollo: Cookies seguras desactivadas")

    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Protección CSRF

    # Configuración de codificación UTF-8
    app.config["JSON_AS_ASCII"] = False

    # Middleware para asegurar UTF-8 en todas las respuestas
    @app.after_request
    def after_request(response):
        response.headers["Content-Type"] = response.headers.get(
            "Content-Type", "text/html"
        )
        if "charset" not in response.headers.get("Content-Type", ""):
            if response.headers["Content-Type"].startswith("application/json"):
                response.headers["Content-Type"] = "application/json; charset=utf-8"
            elif response.headers["Content-Type"].startswith("text/html"):
                response.headers["Content-Type"] = "text/html; charset=utf-8"
        return response

    # Configuración de base de datos
    # Para desarrollo: SQLite
    # Para producción GCP: Cloud SQL PostgreSQL

    db_type = os.getenv("DB_TYPE", "sqlite")  # 'sqlite' o 'postgresql'

    if db_type == "postgresql":
        # Obtener DB_PASSWORD desde Secret Manager (producción) o .env (desarrollo)
        db_password = get_secret_or_env(
            secret_id="gmao-db-password", env_var="DB_PASSWORD", default=""
        )

        # Detectar si estamos en GCP App Engine
        if os.getenv("GAE_ENV", "").startswith("standard"):
            # Configuración Cloud SQL para App Engine
            db_user = os.getenv("DB_USER", "postgres")
            db_name = os.getenv("DB_NAME", "postgres")
            db_host = os.getenv(
                "DB_HOST", "/cloudsql/gmao-sistema:us-central1:gmao-postgres"
            )

            app.config["SQLALCHEMY_DATABASE_URI"] = (
                f"postgresql+psycopg2://{db_user}:{db_password}@/{db_name}?host={db_host}"
            )
        else:
            # Configuración PostgreSQL estándar (desarrollo/producción externa)
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME", "gmao_db")
            db_user = os.getenv("DB_USER", "postgres")

            app.config["SQLALCHEMY_DATABASE_URI"] = (
                f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            )
    else:
        # Configuración SQLite para desarrollo
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../instance/database.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Configuración para uploads de archivos
    app.config["UPLOAD_FOLDER"] = os.path.join(base_dir, "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB máximo

    # Crear directorio de uploads si no existe
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Configuración de URL del servidor
    app.config["SERVER_URL"] = os.getenv("SERVER_URL", "http://localhost:5000")

    # Configuración de email (opcional para desarrollo)
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", "587"))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "")

    # MAIL_PASSWORD desde Secret Manager (producción) o .env (desarrollo)
    app.config["MAIL_PASSWORD"] = get_secret_or_env(
        secret_id="gmao-mail-password", env_var="MAIL_PASSWORD", default=""
    )

    app.config["ADMIN_EMAILS"] = os.getenv("ADMIN_EMAILS", "")

    db.init_app(app)

    # Inicializar Flask-Migrate
    from app.extensions import migrate

    migrate.init_app(app, db)
    app.logger.info("✅ Flask-Migrate inicializado")

    # Inicializar CSRF Protection
    from app.extensions import csrf

    csrf.init_app(app)
    app.logger.info("✅ CSRF Protection inicializado")

    # Inicializar Rate Limiting
    from app.extensions import limiter

    limiter.init_app(app)
    app.logger.info("✅ Rate Limiting inicializado")

    # Inicializar LoginManager
    login_manager = LoginManager()
    login_manager.login_view = (
        "usuarios_controller.login"  # Ruta de login en el controlador de usuarios
    )
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.usuario import Usuario
        from app.extensions import db
        from sqlalchemy import text
        import logging

        logger = logging.getLogger(__name__)

        try:
            logger.debug(f"Loading user with ID: {user_id}")

            # Convertir user_id a int y validar
            if not user_id or str(user_id).strip() == "":
                logger.warning("User ID is empty or None")
                return None

            uid = int(user_id)
            if uid <= 0:
                logger.warning(f"Invalid user ID: {uid}")
                return None

            # Verificar conexión a BD antes de consultar
            try:
                db.session.execute(text("SELECT 1"))
            except Exception as e:
                logger.error(f"Database connection error: {e}")
                # Si hay error de BD, intentar rollback y reconnect
                db.session.rollback()
                return None

            user = Usuario.query.get(uid)
            if user:
                if user.activo:
                    logger.debug(f"User {user.username} loaded successfully")
                    return user
                else:
                    logger.warning(f"User {user.username} is inactive")
            else:
                logger.warning(f"User with ID {uid} not found")

            return None

        except (ValueError, TypeError) as e:
            logger.error(f"Invalid user_id format: {user_id}, error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error loading user {user_id}: {e}")
            db.session.rollback()
            return None

    # Registrar blueprints de rutas
    from app.routes.web import web_bp
    from app.routes.activos import activos_bp
    from app.routes.ordenes import ordenes_bp
    from app.routes.recambios import recambios_bp
    from app.routes.inventario import inventario_bp
    from app.routes.planes import planes_bp
    from app.routes.estadisticas import estadisticas_bp
    from app.routes.proveedores import proveedores_bp
    from app.routes.categorias import categorias_bp, categorias_web_bp
    from app.routes.calendario import calendario_bp
    from app.routes.usuarios import usuarios_bp
    from app.routes.solicitudes import solicitudes_bp

    # Registrar controladores
    from app.controllers.usuarios_controller import usuarios_controller
    from app.controllers.solicitudes_admin_controller import solicitudes_admin_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(activos_bp)
    app.register_blueprint(ordenes_bp)
    app.register_blueprint(recambios_bp, url_prefix="/api")
    app.register_blueprint(inventario_bp)
    app.register_blueprint(planes_bp)
    app.register_blueprint(estadisticas_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(categorias_web_bp)
    app.register_blueprint(calendario_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(solicitudes_bp)
    app.register_blueprint(solicitudes_admin_bp)
    app.register_blueprint(usuarios_controller)

    # Registrar blueprint de cron (tareas programadas)
    from app.routes.cron import cron_bp

    app.register_blueprint(cron_bp)
    app.logger.info("Blueprint de cron registrado")

    # Middleware para verificar sesión
    # @app.before_request
    # def check_session():
    #     from flask_login import current_user
    #     import logging

    #     if request.endpoint and not request.endpoint.startswith("static"):
    #         app.logger.debug(
    #             f"Petición a: {request.endpoint}, Usuario autenticado: {current_user.is_authenticated}"
    #         )
    #         if hasattr(current_user, "id"):
    #             app.logger.debug(f"ID usuario actual: {current_user.id}")
    #         if hasattr(current_user, "username"):
    #             app.logger.debug(f"Username usuario actual: {current_user.username}")

    # Manejadores de errores centralizados
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"Página no encontrada: {error}")
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Error interno del servidor: {error}")
        db.session.rollback()
        return render_template("500.html"), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f"Acceso prohibido: {error}")
        return render_template("403.html"), 403

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.error(f"Error inesperado: {error}", exc_info=True)
        db.session.rollback()
        return render_template("500.html"), 500

    # Los blueprints se registran automáticamente
    # Solo verificar que los blueprints críticos estén disponibles
    try:
        from app.routes.estadisticas import estadisticas_bp

        print("[OK] Blueprint de estadísticas disponible")
    except ImportError as e:
        print(f"[ERROR] Error importando blueprint de estadísticas: {e}")

    return app
