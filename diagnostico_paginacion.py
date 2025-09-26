#!/usr/bin/env python3
"""
Diagnóstico específico para el problema de paginación en personal
"""

import requests
import time

BASE_URL = "http://127.0.0.1:5000"


def diagnosticar_personal():
    print("🔍 DIAGNÓSTICO DE PAGINACIÓN EN PERSONAL")
    print("=" * 60)

    try:
        # 1. Verificar accesibilidad de la página
        print("1. Verificando página principal...")
        response = requests.get(f"{BASE_URL}/personal/", timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code != 200:
            print("   ❌ La página no es accesible")
            return

        content = response.text
        print("   ✅ Página accesible")

        # 2. Verificar elementos clave en HTML
        print("\n2. Verificando elementos HTML...")

        checks = [
            ("paginacion-personal", "   Contenedor de paginación"),
            ("tbody-personal", "   Tabla tbody de empleados"),
            ("contador-empleados", "   Contador de empleados"),
            ("pagination.js", "   Script pagination.js incluido"),
            ("personal.js", "   Script personal.js incluido"),
        ]

        for check, desc in checks:
            if check in content:
                print(f"   ✅ {desc}")
            else:
                print(f"   ❌ {desc} - NO ENCONTRADO")

        # 3. Verificar scripts individuales
        print("\n3. Verificando scripts JavaScript...")

        scripts = [
            ("/static/js/pagination.js", "pagination.js"),
            ("/static/js/personal.js", "personal.js"),
        ]

        for script_url, name in scripts:
            try:
                script_response = requests.get(f"{BASE_URL}{script_url}", timeout=5)
                if script_response.status_code == 200:
                    print(f"   ✅ {name} accesible ({len(script_response.text)} chars)")

                    # Verificar contenido específico
                    if "personal.js" in name:
                        if "inicializarPaginacionPersonal" in script_response.text:
                            print(
                                "      ✅ Función inicializarPaginacionPersonal presente"
                            )
                        if "class Pagination" in script_response.text:
                            print(
                                "      ❌ ERROR: Clase Pagination en personal.js (debería estar en pagination.js)"
                            )

                    if "pagination.js" in name:
                        if "class Pagination" in script_response.text:
                            print("      ✅ Clase Pagination presente")
                        else:
                            print("      ❌ Clase Pagination NO encontrada")

                else:
                    print(f"   ❌ {name} - Status {script_response.status_code}")
            except Exception as e:
                print(f"   ❌ Error accediendo a {name}: {e}")

        # 4. Contar filas de empleados en la tabla
        print("\n4. Analizando estructura de tabla...")
        if '<tbody id="tbody-personal">' in content:
            # Contar filas tr dentro del tbody
            tbody_start = content.find('<tbody id="tbody-personal">')
            tbody_end = content.find("</tbody>", tbody_start)
            if tbody_end > tbody_start:
                tbody_content = content[tbody_start:tbody_end]
                filas_count = tbody_content.count("<tr>")
                print(f"   ✅ Encontradas {filas_count} filas de empleados")
                if filas_count == 0:
                    print("   ⚠️  PROBLEMA: No hay datos para paginar")
                elif filas_count <= 10:
                    print("   ⚠️  INFO: Pocas filas - paginación puede no ser necesaria")
            else:
                print("   ❌ No se pudo analizar contenido del tbody")
        else:
            print("   ❌ tbody-personal no encontrado en HTML")

        # 5. Buscar elementos específicos de paginación
        print("\n5. Buscando elementos de paginación...")
        pagination_indicators = [
            ('<div id="paginacion-personal">', "Contenedor paginacion-personal"),
            ("pagination", "Referencias a paginación"),
            ("page-item", "Elementos de página"),
            ("page-link", "Enlaces de página"),
        ]

        for indicator, desc in pagination_indicators:
            if indicator in content:
                count = content.count(indicator)
                print(f"   ✅ {desc}: {count} occurrencias")
            else:
                print(f"   ❌ {desc}: No encontrado")

    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")

    print("\n" + "=" * 60)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("\nSi ves ❌ en elementos clave, ese es el problema.")
    print("Si todo está ✅, el problema está en JavaScript runtime.")


if __name__ == "__main__":
    diagnosticar_personal()
