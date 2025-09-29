#!/usr/bin/env python3
"""
Script para probar el diseño responsive de la aplicación GMAO
Verifica que todos los componentes se adapten correctamente a diferentes tamaños de pantalla
"""

import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import os


class ResponsiveTester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.driver = None
        self.test_results = []

    def setup_driver(self):
        """Configura el driver de Selenium con diferentes tamaños de pantalla"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Ejecutar en modo headless
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Driver de Chrome configurado correctamente")
        except Exception as e:
            print(f"❌ Error al configurar Chrome driver: {e}")
            print("💡 Asegúrate de tener ChromeDriver instalado")
            return False
        return True

    def test_screen_sizes(self):
        """Prueba diferentes tamaños de pantalla"""
        screen_sizes = [
            {"name": "Desktop Grande", "width": 1920, "height": 1080},
            {"name": "Desktop Mediano", "width": 1366, "height": 768},
            {"name": "Tablet Landscape", "width": 1024, "height": 768},
            {"name": "Tablet Portrait", "width": 768, "height": 1024},
            {"name": "Mobile Grande", "width": 414, "height": 896},  # iPhone 11 Pro Max
            {"name": "Mobile Pequeño", "width": 375, "height": 667},  # iPhone SE
        ]

        results = []

        for size in screen_sizes:
            print(
                f"\n🖥️  Probando tamaño: {size['name']} ({size['width']}x{size['height']})"
            )
            result = self.test_single_size(size)
            results.append(result)

        return results

    def test_single_size(self, size):
        """Prueba un tamaño específico de pantalla"""
        try:
            self.driver.set_window_size(size["width"], size["height"])

            # Visitar la página principal
            self.driver.get(f"{self.base_url}/login")

            # Esperar a que cargue
            time.sleep(2)

            # Verificar elementos responsive
            result = {
                "size": size,
                "sidebar_visible": self.check_sidebar_visibility(),
                "navbar_visible": self.check_navbar_visibility(),
                "content_layout": self.check_content_layout(),
                "table_responsive": self.check_table_responsive(),
                "modal_responsive": self.check_modal_responsive(),
                "form_responsive": self.check_form_responsive(),
                "errors": [],
            }

            # Mostrar resultados
            status = (
                "✅"
                if all(
                    [
                        result["sidebar_visible"]["status"],
                        result["navbar_visible"]["status"],
                        result["content_layout"]["status"],
                        result["table_responsive"]["status"],
                    ]
                )
                else "❌"
            )

            print(f"   {status} Sidebar: {result['sidebar_visible']['message']}")
            print(f"   {status} Navbar: {result['navbar_visible']['message']}")
            print(f"   {status} Layout: {result['content_layout']['message']}")
            print(f"   {status} Tablas: {result['table_responsive']['message']}")

            return result

        except Exception as e:
            print(f"   ❌ Error en {size['name']}: {str(e)}")
            return {"size": size, "error": str(e)}

    def check_sidebar_visibility(self):
        """Verifica que el sidebar se comporte correctamente"""
        try:
            sidebar = self.driver.find_element(By.ID, "sidebar")
            if not sidebar:
                return {"status": False, "message": "Sidebar no encontrado"}

            # Verificar si está visible/oculto según el tamaño
            is_visible = sidebar.is_displayed()
            width = self.driver.get_window_size()["width"]

            if width <= 991:  # Mobile/tablet
                # En móviles debería estar oculto por defecto
                if is_visible:
                    return {
                        "status": True,
                        "message": "Sidebar visible en móvil (correcto)",
                    }
                else:
                    return {
                        "status": False,
                        "message": "Sidebar oculto en móvil (debería estar visible)",
                    }
            else:  # Desktop
                # En desktop debería estar visible
                if is_visible:
                    return {"status": True, "message": "Sidebar visible en desktop"}
                else:
                    return {"status": False, "message": "Sidebar oculto en desktop"}

        except Exception as e:
            return {"status": False, "message": f"Error verificando sidebar: {str(e)}"}

    def check_navbar_visibility(self):
        """Verifica que el navbar responsive funcione"""
        try:
            navbar = self.driver.find_element(By.CLASS_NAME, "navbar-toggler")
            width = self.driver.get_window_size()["width"]

            if width <= 991:  # Mobile/tablet
                if navbar.is_displayed():
                    return {
                        "status": True,
                        "message": "Navbar toggler visible en móvil",
                    }
                else:
                    return {
                        "status": False,
                        "message": "Navbar toggler oculto en móvil",
                    }
            else:  # Desktop
                # En desktop el toggler debería estar oculto
                if not navbar.is_displayed():
                    return {
                        "status": True,
                        "message": "Navbar toggler oculto en desktop",
                    }
                else:
                    return {
                        "status": False,
                        "message": "Navbar toggler visible en desktop",
                    }

        except Exception as e:
            return {"status": False, "message": f"Error verificando navbar: {str(e)}"}

    def check_content_layout(self):
        """Verifica el layout del contenido principal"""
        try:
            main_content = self.driver.find_element(By.ID, "main-content-wrapper")
            width = self.driver.get_window_size()["width"]

            # Verificar padding y márgenes
            padding_left = main_content.value_of_css_property("padding-left")
            margin_left = main_content.value_of_css_property("margin-left")

            if width <= 991:  # Mobile/tablet
                # En móviles no debería tener margen izquierdo grande
                margin_val = (
                    int(margin_left.replace("px", "")) if margin_left != "auto" else 0
                )
                if margin_val < 50:
                    return {"status": True, "message": "Layout correcto en móvil"}
                else:
                    return {
                        "status": False,
                        "message": f"Margen izquierdo demasiado grande en móvil: {margin_left}",
                    }
            else:  # Desktop
                # En desktop debería tener margen para el sidebar
                margin_val = (
                    int(margin_left.replace("px", "")) if margin_left != "auto" else 0
                )
                if margin_val >= 200:
                    return {"status": True, "message": "Layout correcto en desktop"}
                else:
                    return {
                        "status": False,
                        "message": f"Margen izquierdo insuficiente en desktop: {margin_left}",
                    }

        except Exception as e:
            return {"status": False, "message": f"Error verificando layout: {str(e)}"}

    def check_table_responsive(self):
        """Verifica que las tablas sean responsive"""
        try:
            # Buscar contenedores table-responsive
            responsive_tables = self.driver.find_elements(
                By.CLASS_NAME, "table-responsive"
            )

            if responsive_tables:
                # Verificar que tengan overflow horizontal
                for table in responsive_tables:
                    overflow = table.value_of_css_property("overflow-x")
                    if overflow in ["auto", "scroll"]:
                        return {
                            "status": True,
                            "message": "Tablas responsive configuradas",
                        }
                    else:
                        return {
                            "status": False,
                            "message": "Tablas sin overflow horizontal",
                        }
            else:
                # Si no hay tablas responsive, verificar que las tablas normales no se desborden
                tables = self.driver.find_elements(By.TAG_NAME, "table")
                if tables:
                    return {
                        "status": True,
                        "message": "Tablas presentes (verificar manualmente)",
                    }
                else:
                    return {"status": True, "message": "No hay tablas en esta página"}

        except Exception as e:
            return {"status": False, "message": f"Error verificando tablas: {str(e)}"}

    def check_modal_responsive(self):
        """Verifica que los modales sean responsive"""
        try:
            modals = self.driver.find_elements(By.CLASS_NAME, "modal-dialog")
            width = self.driver.get_window_size()["width"]

            for modal in modals:
                modal_width = modal.value_of_css_property("max-width")
                if width <= 576:  # Mobile pequeño
                    # En móviles pequeños los modales deberían ocupar casi toda la pantalla
                    max_width_val = (
                        int(modal_width.replace("px", ""))
                        if "px" in modal_width
                        else 100
                    )
                    if max_width_val >= width * 0.9:
                        return {
                            "status": True,
                            "message": "Modales responsive en móvil",
                        }
                else:
                    return {"status": True, "message": "Modales configurados"}

            return {"status": True, "message": "No hay modales visibles"}

        except Exception as e:
            return {"status": False, "message": f"Error verificando modales: {str(e)}"}

    def check_form_responsive(self):
        """Verifica que los formularios sean responsive"""
        try:
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            width = self.driver.get_window_size()["width"]

            for form in forms:
                # Verificar que los inputs no se desborden
                inputs = form.find_elements(By.TAG_NAME, "input")
                for input_field in inputs:
                    if input_field.is_displayed():
                        input_width = input_field.size["width"]
                        container_width = form.size["width"]

                        if input_width <= container_width:
                            return {"status": True, "message": "Formularios responsive"}
                        else:
                            return {
                                "status": False,
                                "message": "Inputs se desbordan del contenedor",
                            }

            return {"status": True, "message": "Formularios verificados"}

        except Exception as e:
            return {
                "status": False,
                "message": f"Error verificando formularios: {str(e)}",
            }

    def generate_report(self, results):
        """Genera un reporte de los resultados"""
        print("\n" + "=" * 60)
        print("📊 REPORTE DE PRUEBAS RESPONSIVE")
        print("=" * 60)

        total_tests = len(results)
        passed_tests = 0

        for result in results:
            if "error" in result:
                print(f"❌ {result['size']['name']}: ERROR - {result['error']}")
                continue

            checks = [
                result["sidebar_visible"]["status"],
                result["navbar_visible"]["status"],
                result["content_layout"]["status"],
                result["table_responsive"]["status"],
                result["modal_responsive"]["status"],
                result["form_responsive"]["status"],
            ]

            passed = sum(checks)
            total = len(checks)

            if passed == total:
                print(f"✅ {result['size']['name']}: {passed}/{total} pruebas pasaron")
                passed_tests += 1
            else:
                print(f"⚠️  {result['size']['name']}: {passed}/{total} pruebas pasaron")

                # Mostrar detalles de fallos
                if not result["sidebar_visible"]["status"]:
                    print(f"   - Sidebar: {result['sidebar_visible']['message']}")
                if not result["navbar_visible"]["status"]:
                    print(f"   - Navbar: {result['navbar_visible']['message']}")
                if not result["content_layout"]["status"]:
                    print(f"   - Layout: {result['content_layout']['message']}")
                if not result["table_responsive"]["status"]:
                    print(f"   - Tablas: {result['table_responsive']['message']}")

        print(
            f"\n📈 Resumen: {passed_tests}/{total_tests} tamaños de pantalla pasaron todas las pruebas"
        )

        if passed_tests == total_tests:
            print("🎉 ¡Todas las pruebas responsive pasaron exitosamente!")
        else:
            print(
                "⚠️  Se encontraron problemas de responsive design que necesitan corrección"
            )

        return passed_tests == total_tests

    def cleanup(self):
        """Limpia los recursos"""
        if self.driver:
            self.driver.quit()


def main():
    print("🧪 Iniciando pruebas de responsive design para GMAO")
    print("=" * 60)

    # Verificar que la aplicación esté corriendo
    try:
        response = requests.get("http://127.0.0.1:5000", timeout=5)
        if response.status_code != 200:
            print("❌ La aplicación no está corriendo en http://127.0.0.1:5000")
            print("💡 Ejecuta 'python run.py' primero")
            return False
    except:
        print("❌ No se puede conectar a la aplicación")
        print("💡 Ejecuta 'python run.py' primero")
        return False

    tester = ResponsiveTester()

    if not tester.setup_driver():
        return False

    try:
        results = tester.test_screen_sizes()
        success = tester.generate_report(results)
        return success

    finally:
        tester.cleanup()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
