from flask import Flask
from app.extensions import db
from flask_login import LoginManager


def create_app():
    import os

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    static_dir = os.path.join(base_dir, "static")
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config["SECRET_KEY"] = "cambia_esto_por_una_clave_secreta_segura_2025"
    # Configuración aquí si es necesario
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../instance/database.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Configuración para uploads de archivos
    app.config["UPLOAD_FOLDER"] = os.path.join(base_dir, "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB máximo

    # Crear directorio de uploads si no existe
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    # Inicializar LoginManager
    login_manager = LoginManager()
    login_manager.login_view = (
        "web.login"  # Cambia esto si tu ruta de login es diferente
    )
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.usuario import Usuario

        return Usuario.query.get(int(user_id))

    # Registrar blueprints de rutas
    from app.routes.web import web_bp
    from app.routes.activos import activos_bp
    from app.routes.ordenes import ordenes_bp
    from app.routes.inventario import inventario_bp
    from app.routes.planes import planes_bp
    from app.routes.estadisticas import estadisticas_bp
    from app.routes.usuarios import usuarios_bp
    from app.routes.proveedores import proveedores_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(activos_bp)
    app.register_blueprint(ordenes_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(planes_bp)
    app.register_blueprint(estadisticas_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(proveedores_bp)

    return app
