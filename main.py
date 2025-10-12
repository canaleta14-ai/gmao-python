#!/usr/bin/env python3
"""
Punto de entrada para Google App Engine
"""
import os
from flask import send_from_directory
from app.factory import create_app

# Crear la aplicación Flask
app = create_app()


# Ruta específica para servir Service Worker desde la raíz (requerimiento PWA)
@app.route("/sw.js")
def service_worker():
    """Servir el Service Worker desde la raíz del dominio"""
    static_folder = app.static_folder or "static"
    return send_from_directory(static_folder, "sw.js")


# Ruta para servir manifest.json desde la raíz (opcional pero recomendado)
@app.route("/manifest.json")
def manifest():
    """Servir el manifest.json desde la raíz del dominio"""
    static_folder = app.static_folder or "static"
    return send_from_directory(static_folder, "manifest.json")


if __name__ == "__main__":
    # Solo para desarrollo local
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
