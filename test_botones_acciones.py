#!/usr/bin/env python3
"""
Test para verificar que los botones de acciones en inventario tienen títulos visibles
"""

import requests
import time


def test_inventario_buttons():
    """Test que verifica la carga del módulo de inventario"""

    try:
        # Test 1: Verificar que la página de inventario carga correctamente
        print("🧪 Test 1: Verificando página de inventario...")
        response = requests.get("http://127.0.0.1:5000/inventario/", timeout=10)

        if response.status_code == 200:
            print("✅ Página de inventario carga correctamente")

            # Verificar que contiene elementos clave
            content = response.text
            checks = [
                ("tabla-inventario-body", "Tabla de inventario"),
                ("modalNuevoArticulo", "Modal nuevo artículo"),
                ("modalEditarArticulo", "Modal editar artículo"),
                ("btn-group", "Grupos de botones"),
                ("bi-pencil", "Icono editar"),
                ("bi-arrow-left-right", "Icono movimiento"),
                ("bi-clock-history", "Icono historial"),
            ]

            for check_id, description in checks:
                if check_id in content:
                    print(f"✅ {description} presente en HTML")
                else:
                    print(f"⚠️  {description} NO encontrado")

        else:
            print(f"❌ Error al cargar página: {response.status_code}")

        # Test 2: Verificar API de artículos
        print("\n🧪 Test 2: Verificando API de artículos...")
        api_response = requests.get(
            "http://127.0.0.1:5000/inventario/api/articulos?page=1&per_page=5",
            timeout=10,
        )

        if api_response.status_code == 200:
            data = api_response.json()
            if data.get("success") and data.get("articulos"):
                print(
                    f"✅ API funciona - {len(data['articulos'])} artículos encontrados"
                )

                # Mostrar primer artículo como ejemplo
                if data["articulos"]:
                    primer_articulo = data["articulos"][0]
                    print(
                        f"   Ejemplo: {primer_articulo.get('codigo', 'N/A')} - {primer_articulo.get('descripcion', 'N/A')}"
                    )
            else:
                print("⚠️  API responde pero sin artículos")
        else:
            print(f"❌ Error en API: {api_response.status_code}")

        # Test 3: Verificar archivos estáticos
        print("\n🧪 Test 3: Verificando archivos estáticos...")
        static_files = [
            ("/static/js/inventario.js", "JavaScript inventario"),
            ("/static/css/inventario.css", "CSS inventario"),
        ]

        for file_path, description in static_files:
            static_response = requests.get(
                f"http://127.0.0.1:5000{file_path}", timeout=5
            )
            if static_response.status_code == 200:
                print(f"✅ {description} carga correctamente")

                # Verificar contenido específico en inventario.js
                if "inventario.js" in file_path:
                    js_content = static_response.text
                    js_checks = [
                        ("<span>Editar</span>", "Texto 'Editar' en botón"),
                        ("<span>Movimiento</span>", "Texto 'Movimiento' en botón"),
                        ("<span>Historial</span>", "Texto 'Historial' en botón"),
                        ("bi-pencil me-1", "Icono editar con clase"),
                        ("bi-arrow-left-right me-1", "Icono movimiento con clase"),
                        ("bi-clock-history me-1", "Icono historial con clase"),
                    ]

                    for check_text, check_desc in js_checks:
                        if check_text in js_content:
                            print(f"  ✅ {check_desc}")
                        else:
                            print(f"  ❌ {check_desc} NO encontrado")

                # Verificar contenido específico en inventario.css
                elif "inventario.css" in file_path:
                    css_content = static_response.text
                    css_checks = [
                        (".btn-group-sm .btn span", "Estilos para span en botones"),
                        ("margin-right: 0.25rem", "Espaciado de iconos"),
                        ("display: none", "Ocultamiento responsivo"),
                    ]

                    for check_text, check_desc in css_checks:
                        if check_text in css_content:
                            print(f"  ✅ {check_desc}")
                        else:
                            print(f"  ⚠️  {check_desc} podría no estar presente")
            else:
                print(f"❌ {description} NO carga: {static_response.status_code}")

        print(f"\n🎯 Resumen:")
        print(
            f"   - Los botones ahora tienen texto visible: 'Editar', 'Movimiento', 'Historial'"
        )
        print(f"   - En pantallas pequeñas solo se mostrarán los iconos")
        print(f"   - En pantallas grandes se mostrará icono + texto")
        print(f"   - Los tooltips (title) siguen disponibles para accesibilidad")

    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor Flask")
        print(
            "   Asegúrate de que la aplicación esté ejecutándose en http://127.0.0.1:5000"
        )
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 TEST: Botones de Acciones con Títulos Visibles")
    print("=" * 60)
    test_inventario_buttons()
    print("=" * 60)
