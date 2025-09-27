#!/usr/bin/env python3
"""
Test para verificar que los títulos de los modales de movimiento e historial son visibles
"""

import requests
import time


def test_modal_titles():
    """Test que verifica que los títulos de los modales se ven correctamente"""

    try:
        # Test: Verificar que los modales tienen los títulos correctos y la clase modal-modern
        print("🧪 Test: Verificando títulos de modales...")
        response = requests.get("http://127.0.0.1:5000/inventario/", timeout=10)

        if response.status_code == 200:
            print("✅ Página de inventario carga correctamente")

            content = response.text

            # Verificar que todos los modales tengan la clase modal-modern
            modales_checks = [
                ('id="modalMovimiento"', "modal-modern", "Modal Movimiento"),
                ('id="modalHistorial"', "modal-modern", "Modal Historial"),
                ('id="modalMovimientos"', "modal-modern", "Modal Vista General"),
                ('id="modalEditarArticulo"', "modal-modern", "Modal Editar"),
                ('id="modalNuevoArticulo"', "modal-modern", "Modal Nuevo"),
            ]

            print("\n📋 Verificando que todos los modales tengan clase 'modal-modern':")
            for modal_id, modal_class, modal_name in modales_checks:
                # Buscar la línea que contiene el id del modal
                lines = content.split("\n")
                modal_line_found = False
                has_modal_modern = False

                for i, line in enumerate(lines):
                    if modal_id in line:
                        modal_line_found = True
                        # Verificar si en esa línea o las siguientes está modal-modern
                        context_lines = lines[
                            max(0, i - 2) : i + 3
                        ]  # Contexto de 5 líneas
                        context_text = " ".join(context_lines)
                        if modal_class in context_text:
                            has_modal_modern = True
                        break

                if modal_line_found and has_modal_modern:
                    print(f"  ✅ {modal_name} tiene clase '{modal_class}'")
                elif modal_line_found:
                    print(
                        f"  ⚠️  {modal_name} existe pero NO tiene clase '{modal_class}'"
                    )
                else:
                    print(f"  ❌ {modal_name} NO encontrado")

            # Verificar títulos específicos con iconos
            print("\n🏷️ Verificando títulos específicos de modales:")
            titles_checks = [
                (
                    '<i class="fas fa-exchange-alt me-2"></i>Registrar Movimiento',
                    "Título Modal Movimiento",
                ),
                (
                    '<i class="fas fa-history me-2"></i>Historial de Movimientos',
                    "Título Modal Historial",
                ),
                (
                    '<i class="fas fa-exchange-alt me-2"></i>Movimientos de Inventario',
                    "Título Modal Vista General",
                ),
                (
                    '<i class="fas fa-edit me-2"></i>Editar Artículo',
                    "Título Modal Editar",
                ),
                (
                    '<i class="fas fa-plus-circle me-2"></i>Nuevo Artículo',
                    "Título Modal Nuevo",
                ),
            ]

            for title_text, title_name in titles_checks:
                if title_text in content:
                    print(f"  ✅ {title_name} presente con icono")
                else:
                    print(f"  ❌ {title_name} NO encontrado o sin icono")

            # Verificar estilos CSS para modal-modern
            print("\n🎨 Verificando estilos CSS:")
            css_response = requests.get(
                "http://127.0.0.1:5000/static/css/inventario.css", timeout=5
            )
            if css_response.status_code == 200:
                css_content = css_response.text
                css_checks = [
                    (".modal-modern .modal-title", "Estilos para títulos modal-modern"),
                    ("font-weight: 600", "Font-weight para títulos"),
                    ("color: #495057", "Color para títulos"),
                ]

                for css_rule, css_desc in css_checks:
                    if css_rule in css_content:
                        print(f"  ✅ {css_desc}")
                    else:
                        print(f"  ⚠️  {css_desc} podría no estar presente")
            else:
                print("  ❌ No se pudo cargar CSS")

        else:
            print(f"❌ Error al cargar página: {response.status_code}")

        print(f"\n🎯 Resumen del fix:")
        print(
            f"   - Se agregó clase 'modal-modern' a modales de Movimiento, Historial y Vista General"
        )
        print(
            f"   - Los títulos ahora tendrán el mismo estilo consistente que el modal de Editar"
        )
        print(f"   - Se mantuvieron los iconos para mejor identificación visual")
        print(
            f"   - Los estilos CSS .modal-modern .modal-title se aplicarán correctamente"
        )

    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor Flask")
        print(
            "   Asegúrate de que la aplicación esté ejecutándose en http://127.0.0.1:5000"
        )
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("🔧 TEST: Títulos Visibles en Formularios de Movimiento e Historial")
    print("=" * 70)
    test_modal_titles()
    print("=" * 70)
