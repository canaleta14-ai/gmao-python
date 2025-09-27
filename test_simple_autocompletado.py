#!/usr/bin/env python3
"""
Test simple para verificar autocompletado de artículos
"""

from app.factory import create_app
import webbrowser
import time
from threading import Timer


def test_simple_autocompletado():
    print("🧪 Test Simple: Autocompletado de Artículos")
    print("=" * 50)

    app = create_app()

    print("✅ Aplicación creada")
    print("🌐 Abriendo navegador en http://localhost:5000/inventario")
    print("")
    print("📋 PASOS PARA PROBAR:")
    print("1. Hacer login si es necesario")
    print("2. Hacer clic en 'Nuevo Movimiento' (botón azul)")
    print("3. En el campo 'Artículo', escribir algunas letras (ej: 'fil')")
    print("4. Verificar que aparezcan sugerencias de artículos")
    print("5. Seleccionar un artículo de las sugerencias")
    print("6. Verificar que se muestre la información de stock")
    print("")
    print("🔍 Problemas posibles:")
    print("- Si no aparecen sugerencias: Revisar consola del navegador")
    print("- Si hay error 'AutoComplete undefined': Falta cargar autocomplete.js")
    print("- Si la API falla: Verificar endpoint /inventario/api/articulos")
    print("")

    def abrir_navegador():
        time.sleep(2)
        webbrowser.open("http://localhost:5000/inventario")

    Timer(1, abrir_navegador).start()

    try:
        app.run(debug=True, port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido")
        print("✅ Test completado")


if __name__ == "__main__":
    test_simple_autocompletado()
