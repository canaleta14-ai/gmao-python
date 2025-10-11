#!/usr/bin/env python3
"""
Configuración de base de datos PostgreSQL para producción
"""

import os
import sys


def configure_postgresql():
    """Configurar conexión a PostgreSQL en Cloud SQL"""

    print("🗄️ Configurando conexión a PostgreSQL...")

    # Configuración para Cloud SQL
    if os.getenv("GAE_ENV", "").startswith("standard"):
        # En App Engine
        db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
        instance_connection_name = f"disfood-gmao:us-central1:gmao-db"
        db_socket_path = f"{db_socket_dir}/{instance_connection_name}"

        database_url = (
            f"postgresql+psycopg2://{os.environ['DB_USER']}:"
            f"{os.environ['DB_PASSWORD']}@/"
            f"{os.environ['DB_NAME']}?host={db_socket_path}"
        )
    else:
        # En local o con Cloud SQL Proxy
        database_url = (
            f"postgresql+psycopg2://{os.environ.get('DB_USER', 'gmao_user')}:"
            f"{os.environ.get('DB_PASSWORD', 'password')}@"
            f"{os.environ.get('DB_HOST', 'localhost')}:"
            f"{os.environ.get('DB_PORT', '5432')}/"
            f"{os.environ.get('DB_NAME', 'gmao_production')}"
        )

    os.environ["DATABASE_URL"] = database_url
    print(f"✅ DATABASE_URL configurada")

    return database_url


def init_production_database():
    """Inicializar base de datos con tablas y datos básicos"""

    try:
        from app.factory import create_app
        from app.extensions import db
        from app.models.usuario import Usuario
        from app.models.categoria import Categoria
        from werkzeug.security import generate_password_hash

        app = create_app()

        with app.app_context():
            print("🔧 Creando tablas de base de datos...")
            db.create_all()

            # Crear usuario administrador si no existe
            admin = Usuario.query.filter_by(username="admin").first()
            if not admin:
                print("👤 Creando usuario administrador...")
                admin_password = os.environ.get("ADMIN_INITIAL_PASSWORD", "Admin123!")
                admin = Usuario(
                    username="admin",
                    email="admin@disfood.com",
                    password_hash=generate_password_hash(admin_password),
                    rol="admin",
                )
                db.session.add(admin)
                db.session.commit()
                print(f"✅ Usuario admin creado con password: {admin_password}")

            # Crear categorías básicas si no existen
            categorias_basicas = [
                "Equipos de Cocina",
                "Refrigeración",
                "Sistemas de Ventilación",
                "Equipos de Limpieza",
                "Mobiliario",
                "Sistemas Eléctricos",
                "Fontanería",
                "Otros",
            ]

            categorias_existentes = Categoria.query.count()
            if categorias_existentes == 0:
                print("📂 Creando categorías básicas...")
                for nombre in categorias_basicas:
                    categoria = Categoria(
                        nombre=nombre, descripcion=f"Categoría para {nombre.lower()}"
                    )
                    db.session.add(categoria)

                db.session.commit()
                print(f"✅ {len(categorias_basicas)} categorías creadas")

            print("✅ Base de datos inicializada correctamente")

    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        sys.exit(1)


if __name__ == "__main__":
    configure_postgresql()
    init_production_database()
