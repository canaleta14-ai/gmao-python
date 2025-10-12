#!/usr/bin/env python3
"""
Script para probar la integración FIFO en desarrollo
"""
import os
import sys

# Configurar entorno de desarrollo
os.environ["FLASK_ENV"] = "development"
os.environ["FLASK_DEBUG"] = "1"
os.environ["SECRET_KEY"] = (
    "development-secret-key-for-testing-fifo-integration-very-long-key-to-meet-requirements"
)

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app

    app = create_app()

    # Configuraciones adicionales para desarrollo
    app.config.update(
        {
            "SECRET_KEY": "development-secret-key-for-testing-fifo-integration-very-long-key-to-meet-requirements",
            "DEBUG": True,
            "TESTING": False,
            "WTF_CSRF_ENABLED": False,  # Deshabilitar CSRF para testing
        }
    )

    print("🚀 Servidor de desarrollo iniciado")
    print("📍 URL: http://127.0.0.1:5000")
    print("🏷️  Prueba FIFO: http://127.0.0.1:5000/inventario")
    print("🔧 Modo: Desarrollo (DEBUG=True)")

    if __name__ == "__main__":
        app.run(
            debug=True,
            host="127.0.0.1",
            port=5000,
            use_reloader=True,
            use_debugger=True,
        )

except Exception as e:
    print(f"❌ Error al iniciar servidor: {e}")
    import traceback

    traceback.print_exc()
