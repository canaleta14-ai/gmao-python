#!/usr/bin/env python3
"""
Script para ejecutar GMAO en modo local sin debug (más estable para pruebas)
"""

import os
import sys


def main():
    print("🚀 Iniciando GMAO local (modo estable para pruebas)...")

    # Limpiar variables de Google Cloud
    google_vars = ["GOOGLE_CLOUD_PROJECT", "GAE_ENV", "GOOGLE_APPLICATION_CREDENTIALS"]
    for var in google_vars:
        if var in os.environ:
            del os.environ[var]
            print(f"   Eliminada variable: {var}")

    # Configurar variables locales
    os.environ["SECRETS_PROVIDER"] = "env"
    os.environ["FLASK_ENV"] = "production"  # Sin debug para estabilidad
    os.environ["DB_TYPE"] = "sqlite"
    os.environ["SECRET_KEY"] = "tu-clave-secreta-local-muy-segura"
    os.environ["DATABASE_URL"] = "sqlite:///C:/Users/canal/gmao-sistema/gmao_local.db"
    os.environ["FORCE_LOCAL_STORAGE"] = "true"  # Forzar almacenamiento local

    print("✅ Variables configuradas:")
    print("   SECRETS_PROVIDER: env")
    print("   FLASK_ENV: production (modo estable)")
    print("   DB_TYPE: sqlite")
    print("   FORCE_LOCAL_STORAGE: true")

    # Importar y ejecutar la aplicación
    try:
        from app.factory import create_app

        app = create_app()

        print("✅ Aplicación iniciada correctamente")
        print("🌐 Accesible en: http://localhost:5000")
        print("👤 Usuario: admin | 🔑 Contraseña: admin123")
        print("🔧 Presiona Ctrl+C para detener")
        print("-" * 50)

        # Ejecutar sin debug para mayor estabilidad
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida por el usuario")
    except Exception as e:
        print(f"❌ Error al iniciar aplicación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
