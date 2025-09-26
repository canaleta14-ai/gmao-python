#!/usr/bin/env python3
"""
Test para verificar que la paginación de personal funciona correctamente
"""

import requests
import time

BASE_URL = "http://127.0.0.1:5000"


def test_personal_page():
    """Verifica que la página de personal sea accesible"""
    print("🧪 Probando accesibilidad de página de personal...")

    try:
        response = requests.get(f"{BASE_URL}/personal", timeout=10)

        if response.status_code == 200:
            print("✅ Página de personal accesible (Status 200)")

            # Verificar elementos clave en la página
            content = response.text
            checks = [
                ("pagination.js", "Script de paginación incluido"),
                ("paginacion-personal", "Contenedor de paginación presente"),
                ("contador-empleados", "Contador de empleados presente"),
                ("inicializarPaginacionPersonal", "Función de inicialización presente"),
            ]

            for check, description in checks:
                if check in content:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description} - NO ENCONTRADO")

        else:
            print(f"❌ Error: Status {response.status_code}")

    except Exception as e:
        print(f"❌ Error de conexión: {e}")


def test_scripts_accessibility():
    """Verifica que los scripts necesarios sean accesibles"""
    scripts = [
        ("/static/js/personal.js", "JavaScript de personal"),
        ("/static/js/pagination.js", "JavaScript de paginación"),
    ]

    print("\n🧪 Verificando accesibilidad de scripts...")

    for script_url, description in scripts:
        try:
            response = requests.get(f"{BASE_URL}{script_url}", timeout=5)
            if response.status_code == 200:
                size = len(response.text)
                print(f"✅ {description} accesible ({size} caracteres)")

                # Verificar contenido específico
                if "personal.js" in script_url:
                    if "inicializarPaginacionPersonal" in response.text:
                        print("✅   - Función inicializarPaginacionPersonal encontrada")
                    if "paginacionPersonal" in response.text:
                        print("✅   - Variable paginacionPersonal encontrada")

            else:
                print(f"❌ {description} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ Error accediendo a {description}: {e}")


if __name__ == "__main__":
    print("🚀 TESTING PAGINACIÓN DE PERSONAL")
    print("=" * 50)

    test_personal_page()
    test_scripts_accessibility()

    print("\n=" * 50)
    print("✅ TESTS COMPLETADOS")
    print()
    print("💡 INSTRUCCIONES PARA VERIFICAR:")
    print("1. Abrir: http://127.0.0.1:5000/personal")
    print("2. Abrir DevTools (F12) y ir a Console")
    print("3. Buscar logs como:")
    print("   - 'Personal module loaded'")
    print("   - '🔧 Inicializando paginación de personal...'")
    print("   - '✅ Paginación inicializada: X páginas, Y empleados'")
    print("4. Verificar que los botones de paginación no redirijan al dashboard")
    print("5. Cambiar de página y verificar que se mantiene en /personal")
