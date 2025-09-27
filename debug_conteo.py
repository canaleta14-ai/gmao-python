#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.controllers.inventario_controller import procesar_conteo_fisico

app = create_app()

with app.app_context():
    try:
        print("Iniciando procesamiento del conteo 13...")
        # Los parámetros correctos son: conteo_id, stock_fisico, observaciones, usuario
        resultado = procesar_conteo_fisico(13, 5, "", "admin")
        print(f"Resultado: {resultado}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()

        traceback.print_exc()
