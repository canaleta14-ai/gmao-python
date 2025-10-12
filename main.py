#!/usr/bin/env python3
"""
Punto de entrada para Google App Engine
"""
import os
from app.factory import create_app

# Crear la aplicación Flask
app = create_app()

if __name__ == "__main__":
    # Solo para desarrollo local
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
