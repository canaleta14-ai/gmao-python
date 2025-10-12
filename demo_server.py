#!/usr/bin/env python
"""
Script para iniciar el servidor en modo desarrollo para ver los artículos de prueba FIFO
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuración de desarrollo
os.environ["FLASK_ENV"] = "development"
os.environ["SECRET_KEY"] = (
    "development-secret-key-for-testing-fifo-articles-demo-1234567890"
)
os.environ["DATABASE_URL"] = "sqlite:///gmao.db"

from app import create_app

if __name__ == "__main__":
    app = create_app()
    print("\n" + "=" * 60)
    print("🚀 SERVIDOR GMAO INICIADO EN MODO DESARROLLO")
    print("=" * 60)
    print(f"📊 URL Principal: http://127.0.0.1:5000")
    print(f"📦 Demo FIFO: http://127.0.0.1:5000/lotes/demo")
    print(f"🔗 Sistema Lotes: http://127.0.0.1:5000/lotes/")
    print("=" * 60)
    print("Para ver los artículos de prueba FIFO, visite:")
    print("👉 http://127.0.0.1:5000/lotes/demo")
    print("=" * 60)
    print("Presione Ctrl+C para detener el servidor\n")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000,
        use_reloader=False,  # Evitar reinicios automáticos
    )
