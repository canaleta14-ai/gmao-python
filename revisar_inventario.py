#!/usr/bin/env python3
"""
Script para verificar artículos de prueba en base de datos local vs cloud
"""

import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def verificar_inventario_orm():
    """Usar ORM de SQLAlchemy para verificar inventario"""

    from app import create_app
    from app.models import Inventario, db

    app = create_app()

    with app.app_context():
        print("📦 VERIFICACIÓN DEL INVENTARIO USANDO ORM")
        print("=" * 55)

        # Obtener información de conexión
        try:
            from app.config import Config

            db_config = os.environ.get("DATABASE_URL", "No configurado")
            if "cloudsql" in db_config:
                db_tipo = "🌐 CLOUD (Google Cloud SQL)"
            elif "localhost" in db_config or "127.0.0.1" in db_config:
                db_tipo = "💻 LOCAL"
            else:
                db_tipo = "❓ DESCONOCIDO"

            print(f"🔗 Conexión: {db_tipo}")
            print(f"🔧 DB URL: {db_config[:50]}...")
            print()
        except:
            print("⚠️  No se pudo determinar el tipo de base de datos")
            print()

        try:
            # Contar todos los artículos
            total_articulos = Inventario.query.count()
            print(f"📊 Total de artículos en inventario: {total_articulos}")

            if total_articulos == 0:
                print("✅ El inventario está completamente vacío")
                return

            # Buscar artículos que parezcan de prueba usando ORM
            articulos_prueba = Inventario.query.filter(
                db.or_(
                    Inventario.codigo.ilike("%prueba%"),
                    Inventario.codigo.ilike("%test%"),
                    Inventario.codigo.ilike("%demo%"),
                    Inventario.nombre.ilike("%prueba%"),
                    Inventario.nombre.ilike("%test%"),
                    Inventario.nombre.ilike("%demo%"),
                    Inventario.codigo.like("P-%"),
                    Inventario.codigo.like("T-%"),
                    Inventario.codigo.like("TEST-%"),
                    Inventario.codigo.like("DEMO-%"),
                )
            ).all()

            print(f"🧪 Artículos de prueba encontrados: {len(articulos_prueba)}")

            if len(articulos_prueba) > 0:
                print("\n📋 ARTÍCULOS DE PRUEBA DETECTADOS:")
                print("-" * 60)
                for art in articulos_prueba:
                    print(f"ID: {art.id:3d} | {art.codigo:15s} | {art.nombre[:30]:30s}")
                print("-" * 60)
            else:
                print("✅ No se encontraron artículos de prueba")

            # Mostrar algunos artículos normales para verificar
            articulos_normales = Inventario.query.limit(5).all()
            if len(articulos_normales) > 0:
                print(f"\n📋 MUESTRA DE ARTÍCULOS NORMALES (primeros 5):")
                print("-" * 60)
                for art in articulos_normales:
                    print(f"ID: {art.id:3d} | {art.codigo:15s} | {art.nombre[:30]:30s}")
                print("-" * 60)

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback

            traceback.print_exc()


def verificar_variables_entorno():
    """Verificar variables de entorno de base de datos"""

    print("🔧 CONFIGURACIÓN DE BASE DE DATOS")
    print("=" * 40)

    variables_db = [
        "DATABASE_URL",
        "DB_TYPE",
        "DB_HOST",
        "DB_NAME",
        "DB_USER",
        "GOOGLE_CLOUD_PROJECT",
    ]

    for var in variables_db:
        valor = os.environ.get(var, "No configurado")
        print(f"{var}: {valor}")

    print()

    # Determinar tipo de base de datos
    db_url = os.environ.get("DATABASE_URL", "")
    db_host = os.environ.get("DB_HOST", "")

    if "cloudsql" in db_url or "cloudsql" in db_host:
        print("🌐 CONECTADO A: Google Cloud SQL (Producción)")
    elif "localhost" in db_url or "127.0.0.1" in db_url or "localhost" in db_host:
        print("💻 CONECTADO A: Base de datos local")
    elif not db_url and not db_host:
        print("❓ CONFIGURACIÓN INDEFINIDA: Posiblemente usando SQLite local")
    else:
        print(f"❓ CONFIGURACIÓN DESCONOCIDA")

    print()


if __name__ == "__main__":
    print("🔍 VERIFICACIÓN DE ARTÍCULOS DE PRUEBA")
    print("=" * 50)
    print(f"🕐 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Verificar configuración
    verificar_variables_entorno()

    # Verificar inventario
    verificar_inventario_orm()
