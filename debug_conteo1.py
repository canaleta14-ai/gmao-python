#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.controllers.inventario_controller import procesar_conteo_fisico

app = create_app()

with app.app_context():
    try:
        print("Iniciando procesamiento del conteo 1...")
        # Probemos con stock_fisico diferente para generar una diferencia
        resultado = procesar_conteo_fisico(1, 8, "Prueba con supervisor", "supervisor")
        print(f"Resultado: {resultado}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
