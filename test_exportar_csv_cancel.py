#!/usr/bin/env python3
"""
Test para verificar el comportamiento de cancelar exportación CSV en inventario
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
import webbrowser
import time
from threading import Timer


def test_exportar_csv_cancel():
    """Prueba para verificar que cancelar exportación CSV no deja cargando"""

    print("🧪 Test: Cancelar exportación CSV en inventario")
    print("=" * 50)

    # Crear app
    app = create_app()

    print("✅ Aplicación creada correctamente")
    print("🌐 Iniciando servidor de desarrollo...")
    print("")
    print("📋 INSTRUCCIONES PARA LA PRUEBA:")
    print("1. Se abrirá automáticamente el navegador en /inventario")
    print("2. Haz clic en el botón 'Exportar CSV'")
    print("3. CANCELA la descarga cuando aparezca el diálogo")
    print("4. Verifica que NO se quede cargando artículos indefinidamente")
    print("5. Los artículos deben mostrarse normalmente")
    print("")
    print("🔍 Qué buscar:")
    print("   - ❌ ANTES: Al cancelar, la tabla se quedaba con spinner de carga")
    print(
        "   - ✅ DESPUÉS: Al cancelar, la tabla vuelve a mostrar los artículos normalmente"
    )
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
        print("✅ Test completado")


if __name__ == "__main__":
    test_exportar_csv_cancel()
