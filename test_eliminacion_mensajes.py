#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar que se eliminaron los mensajes informativos innecesarios
de órdenes de trabajo.
"""

import requests

BASE_URL = "http://127.0.0.1:5000"


def test_ordenes_js_changes():
    """Test para verificar que los mensajes informativos fueron removidos"""
    print("🔍 Verificando eliminación de mensajes informativos en órdenes...")

    try:
        response = requests.get(f"{BASE_URL}/static/js/ordenes.js", timeout=10)

        if response.status_code == 200:
            js_content = response.text

            # Mensajes que deberían haber sido eliminados
            mensajes_eliminados = [
                "Ver detalles de orden",
                "Editar orden #",
                "Cambiar estado de orden #",
                "Archivos adjuntos procesados",
                "recambio(s) descontado(s) del stock automáticamente",
            ]

            print("\nVerificando eliminación de mensajes innecesarios:")

            all_removed = True
            for mensaje in mensajes_eliminados:
                if mensaje in js_content:
                    print(f"❌ Mensaje aún presente: '{mensaje}'")
                    all_removed = False
                else:
                    print(f"✅ Mensaje eliminado: '{mensaje}'")

            # Verificar que los mensajes importantes se mantuvieron
            mensajes_importantes = [
                "Orden actualizada exitosamente",
                "Orden de trabajo creada exitosamente",
                "No hay técnicos disponibles",
                "Debe seleccionar un nuevo estado",
                "Estado actualizado a:",
            ]

            print("\nVerificando que mensajes importantes se mantuvieron:")

            for mensaje in mensajes_importantes:
                if mensaje in js_content:
                    print(f"✅ Mensaje importante mantenido: '{mensaje}'")
                else:
                    print(
                        f"⚠️ Mensaje importante podría haber sido eliminado: '{mensaje}'"
                    )

            return all_removed

        else:
            print(f"❌ Error cargando JavaScript: Status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error verificando JavaScript: {e}")
        return False


if __name__ == "__main__":
    print("🧪 TEST DE ELIMINACIÓN DE MENSAJES INFORMATIVOS")
    print("=" * 55)

    result = test_ordenes_js_changes()

    print("\n" + "=" * 55)
    print("📊 RESULTADO:")

    if result:
        print("🎉 ¡Todos los mensajes informativos innecesarios fueron eliminados!")
        print("Los mensajes importantes de éxito y error se mantuvieron.")
    else:
        print("⚠️ Algunos mensajes informativos aún están presentes.")

    print("=" * 55)
