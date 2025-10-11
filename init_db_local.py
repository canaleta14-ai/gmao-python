#!/usr/bin/env python3
"""
Script para inicializar la base de datos SQLite local
Crea todas las tablas y datos iniciales necesarios
"""

import os
import sys

# Configurar entorno para desarrollo local
os.environ["FLASK_ENV"] = "development"
os.environ["DB_TYPE"] = "sqlite"
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gmao_local.db"
os.environ["SECRET_KEY"] = (
    "local-development-secret-key-muy-segura-123456789-abcdefghijklmnopqrstuvwxyz-DESARROLLO"
)
os.environ["SECRETS_PROVIDER"] = "env"
if "GAE_ENV" in os.environ:
    del os.environ["GAE_ENV"]

from app.factory import create_app
from app.extensions import db


def init_database():
    """Inicializa la base de datos SQLite con todas las tablas"""
    print("🔄 Inicializando base de datos SQLite...")

    app = create_app()

    with app.app_context():
        try:
            # Eliminar todas las tablas existentes
            print("   Eliminando tablas existentes...")
            db.drop_all()

            # Crear todas las tablas
            print("   Creando nuevas tablas...")
            db.create_all()

            # Crear usuario admin por defecto
            from app.models.usuario import Usuario

            # Verificar si ya existe admin
            admin_exists = Usuario.query.filter_by(username="admin").first()
            if not admin_exists:
                print("   Creando usuario administrador...")
                admin = Usuario(
                    username="admin",
                    email="admin@gmao.local",
                    nombre="Administrator",
                    rol="administrador",
                    activo=True,
                )
                admin.set_password("admin123")
                db.session.add(admin)
                db.session.commit()
                print("   ✅ Usuario admin creado: admin/admin123")
            else:
                print("   ✅ Usuario admin ya existe")

            # Crear algunas categorías básicas
            from app.models.categoria import Categoria

            if not Categoria.query.first():
                print("   Creando categorías básicas...")
                categorias = [
                    Categoria(
                        nombre="Herramientas",
                        prefijo="HER",
                        descripcion="Herramientas de trabajo",
                        color="#28a745",
                    ),
                    Categoria(
                        nombre="Repuestos",
                        prefijo="REP",
                        descripcion="Repuestos y componentes",
                        color="#17a2b8",
                    ),
                    Categoria(
                        nombre="Materiales",
                        prefijo="MAT",
                        descripcion="Materiales de construcción",
                        color="#ffc107",
                    ),
                    Categoria(
                        nombre="Equipos",
                        prefijo="EQU",
                        descripcion="Equipos y maquinaria",
                        color="#dc3545",
                    ),
                ]
                for cat in categorias:
                    db.session.add(cat)
                db.session.commit()
                print("   ✅ Categorías básicas creadas")

            print("🎉 ¡Base de datos inicializada correctamente!")
            print("🌐 Puedes acceder a: http://localhost:5000")
            print("👤 Usuario: admin | Contraseña: admin123")

        except Exception as e:
            print(f"❌ Error inicializando base de datos: {e}")
            return False

    return True


if __name__ == "__main__":
    init_database()
