#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar que los modales de proveedores funcionan correctamente
"""

import requests
import json
import time

# URL base de la aplicación
BASE_URL = "http://127.0.0.1:5000"


def test_proveedores_page():
    """Test para verificar que la página de proveedores carga correctamente"""
    print("🔍 Probando página de proveedores...")

    try:
        response = requests.get(f"{BASE_URL}/proveedores", timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ Página de proveedores carga correctamente")

            # Verificar que contiene elementos del modal
            content = response.text
            checks = [
                "modalProveedor" in content,
                "btnGuardarProveedor" in content,
                "modalProveedorTitle" in content,
                "proveedor-nif" in content,
            ]

            print(f"Modal básico presente: {'✅' if checks[0] else '❌'}")
            print(f"Botón guardar presente: {'✅' if checks[1] else '❌'}")
            print(f"Título del modal presente: {'✅' if checks[2] else '❌'}")
            print(f"Campo NIF presente: {'✅' if checks[3] else '❌'}")

            return all(checks)
        else:
            print(f"❌ Error: Status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False


def test_proveedores_api():
    """Test para verificar que la API de proveedores funciona"""
    print("\n🔍 Probando API de proveedores...")

    try:
        response = requests.get(f"{BASE_URL}/proveedores/api", timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(
                f"✅ API funciona correctamente, proveedores encontrados: {len(data)}"
            )
            return True
        else:
            print(f"❌ Error en API: Status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error de conexión con API: {e}")
        return False


def test_javascript_changes():
    """Test para verificar que los archivos JavaScript están actualizados"""
    print("\n🔍 Verificando cambios en JavaScript...")

    try:
        response = requests.get(f"{BASE_URL}/static/js/proveedores.js", timeout=10)

        if response.status_code == 200:
            js_content = response.text

            checks = [
                "crearModalVerProveedor" in js_content,
                "Detalles del Proveedor" in js_content,
                "<strong>NIF:</strong>" in js_content,
                "editarProveedorDesdeVer" in js_content,
            ]

            print(f"Función crear modal presente: {'✅' if checks[0] else '❌'}")
            print(f"Título modal actualizado: {'✅' if checks[1] else '❌'}")
            print(f"Campo NIF corregido: {'✅' if checks[2] else '❌'}")
            print(f"Función editar desde ver: {'✅' if checks[3] else '❌'}")

            # Verificar que no contiene el texto antiguo "RUT/NIT"
            no_rut_nit = "RUT/NIT" not in js_content
            print(f"RUT/NIT removido: {'✅' if no_rut_nit else '❌'}")

            return all(checks) and no_rut_nit
        else:
            print(f"❌ Error cargando JavaScript: Status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error verificando JavaScript: {e}")
        return False


if __name__ == "__main__":
    print("🧪 INICIANDO TESTS DE MODAL DE PROVEEDORES")
    print("=" * 50)

    # Esperar un momento para asegurar que el servidor esté listo
    time.sleep(2)

    results = []

    # Ejecutar tests
    results.append(test_proveedores_page())
    results.append(test_proveedores_api())
    results.append(test_javascript_changes())

    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE TESTS:")

    passed = sum(results)
    total = len(results)

    print(f"✅ Tests exitosos: {passed}/{total}")

    if passed == total:
        print("🎉 ¡Todos los tests pasaron! Los modales están correctos.")
    else:
        print("⚠️ Algunos tests fallaron. Revisar los cambios.")

    print("=" * 50)
