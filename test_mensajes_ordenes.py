#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar que los mensajes de órdenes ahora aparecen
arriba a la derecha como en el resto de la aplicación.
"""

import requests

BASE_URL = "http://127.0.0.1:5000"


def test_ordenes_mensaje_system():
    """Test para verificar el sistema de mensajes actualizado"""
    print("🔍 Verificando sistema de mensajes de órdenes...")

    try:
        response = requests.get(f"{BASE_URL}/static/js/ordenes.js", timeout=10)

        if response.status_code == 200:
            js_content = response.text

            # Verificar que la nueva función mostrarMensaje existe
            checks = [
                "function mostrarMensaje(" in js_content,
                "position-fixed" in js_content,
                "top: 20px; right: 20px" in js_content,
                "z-index: 1060" in js_content,
                "alert alert-" in js_content,
                "alert-dismissible" in js_content,
            ]

            print("\nVerificando nueva función mostrarMensaje:")
            labels = [
                "Función mostrarMensaje definida",
                "Posicionamiento fijo",
                "Posición superior derecha",
                "Z-index correcto",
                "Clases Bootstrap de alerta",
                "Alerta dismissible",
            ]

            for i, check in enumerate(checks):
                print(f"{'✅' if check else '❌'} {labels[i]}")

            # Verificar que no quedan llamadas a mostrarToast
            no_toast_calls = "mostrarToast(" not in js_content
            print(f"{'✅' if no_toast_calls else '❌'} No quedan llamadas mostrarToast")

            # Verificar que las llamadas se cambiaron a mostrarMensaje
            mensaje_calls = js_content.count("mostrarMensaje(")
            print(f"✅ Encontradas {mensaje_calls} llamadas a mostrarMensaje")

            # Verificar tipos de mensaje correctos
            success_msgs = "'success'" in js_content
            danger_msgs = "'danger'" in js_content
            warning_msgs = "'warning'" in js_content

            print(f"✅ Mensajes de éxito: {'Sí' if success_msgs else 'No'}")
            print(f"✅ Mensajes de error: {'Sí' if danger_msgs else 'No'}")
            print(f"✅ Mensajes de advertencia: {'Sí' if warning_msgs else 'No'}")

            # Verificar que no quedan tipos 'error' (deben ser 'danger')
            no_error_type = "'error'" not in js_content
            print(
                f"{'✅' if no_error_type else '❌'} Tipo 'error' eliminado (ahora 'danger')"
            )

            return all(checks) and no_toast_calls and mensaje_calls > 0

        else:
            print(f"❌ Error cargando JavaScript: Status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error verificando JavaScript: {e}")
        return False


def test_ordenes_page_loads():
    """Test para verificar que la página de órdenes carga correctamente"""
    print("\n🔍 Verificando que la página de órdenes carga...")

    try:
        response = requests.get(f"{BASE_URL}/ordenes", timeout=10)

        if response.status_code == 200:
            print("✅ Página de órdenes carga correctamente")
            return True
        else:
            print(f"❌ Error: Status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False


if __name__ == "__main__":
    print("🧪 TEST DE SISTEMA DE MENSAJES DE ÓRDENES")
    print("=" * 55)

    results = []
    results.append(test_ordenes_mensaje_system())
    results.append(test_ordenes_page_loads())

    print("\n" + "=" * 55)
    print("📊 RESULTADO:")

    passed = sum(results)
    total = len(results)

    print(f"✅ Tests exitosos: {passed}/{total}")

    if passed == total:
        print("🎉 ¡Sistema de mensajes actualizado correctamente!")
        print(
            "Los mensajes ahora aparecen arriba a la derecha como en el resto de la app."
        )
    else:
        print("⚠️ Algunos tests fallaron. Revisar implementación.")

    print("=" * 55)
