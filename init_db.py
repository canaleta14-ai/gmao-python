from app.factory import create_app
from app.extensions import db
from app.models import *  # Import all models so db.create_all() creates all tables
from werkzeug.security import generate_password_hash

# Script para inicializar la base de datos y crear el usuario admin


def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        if Usuario.query.count() == 0:
            admin = Usuario(
                username="admin",
                email="admin@gmao.com",
                password=generate_password_hash("admin123"),
                nombre="Administrador",
                rol="Administrador",
                activo=True,
            )
            db.session.add(admin)
            db.session.commit()
            print("Usuario admin creado: admin / admin123 (contraseña hasheada)")
        else:
            print("La base de datos ya tiene usuarios. No se creó el admin.")


if __name__ == "__main__":
    init_db()
