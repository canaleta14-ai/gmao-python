#!/usr/bin/env python3
"""
Test para verificar el autocompletado de artículos en modal de movimiento
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
import webbrowser
import time
from threading import Timer


def test_autocompletado_movimiento():
    """Prueba para verificar el autocompletado de artículos en movimientos"""

    print("🧪 Test: Autocompletado de artículos en modal de movimiento")
    print("=" * 60)

    # Crear app
    app = create_app()

    print("✅ Aplicación creada correctamente")
    print("🌐 Iniciando servidor de desarrollo...")
    print("")
    print("📋 INSTRUCCIONES PARA LA PRUEBA:")
    print("1. Se abrirá automáticamente el navegador en /inventario")
    print("2. Haz clic en 'Nuevo Movimiento' en la barra superior")
    print("3. En el campo 'Artículo', empieza a escribir para probar el autocompletado")
    print("4. Deberías ver sugerencias de artículos con código, descripción y stock")
    print("5. Selecciona un artículo y cambia el tipo a 'Salida'")
    print("6. Introduce una cantidad para verificar la validación de stock")
    print("")
    print("🔍 Funcionalidades que se probarán:")
    print("   ✨ Autocompletado por código de artículo")
    print("   ✨ Autocompletado por descripción de artículo")
    print("   ✨ Visualización de stock actual")
    print("   ✨ Validación de stock para salidas")
    print("   ✨ Alertas por stock bajo mínimo")
    print("   ✨ Búsqueda por categoría de artículo")
    print("")

    # Abrir navegador después de un pequeño delay
    def abrir_navegador():
        time.sleep(2)
        webbrowser.open("http://localhost:5000/inventario")

    timer = Timer(1, abrir_navegador)
    timer.start()

    try:
        # Ejecutar la aplicación
        app.run(debug=True, port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
        print("✅ Test de autocompletado completado")


if __name__ == "__main__":
    test_autocompletado_movimiento()
