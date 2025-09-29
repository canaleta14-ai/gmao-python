#!/usr/bin/env python3
"""
Script para validar la configuración responsive de la aplicación GMAO
Verifica que los estilos CSS estén correctamente configurados para diferentes tamaños de pantalla
"""

import os
import re
import requests
from pathlib import Path


class ResponsiveValidator:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.issues = []
        self.warnings = []

    def validate_css_responsive(self):
        """Valida las reglas CSS responsive"""
        print("🔍 Validando configuración CSS responsive...")

        css_files = [
            self.project_root / "static" / "css" / "style.css",
            self.project_root / "static" / "css" / "ordenes.css",
            self.project_root / "static" / "css" / "inventario.css",
            self.project_root / "static" / "css" / "usuarios.css",
            self.project_root / "static" / "css" / "proveedores.css",
            self.project_root / "static" / "css" / "preventivo.css",
            self.project_root / "static" / "css" / "login.css",
        ]

        for css_file in css_files:
            if css_file.exists():
                self._validate_css_file(css_file)

    def _validate_css_file(self, css_file):
        """Valida un archivo CSS específico"""
        print(f"  📄 Revisando {css_file.name}...")

        try:
            with open(css_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Verificar media queries
            self._check_media_queries(content, css_file.name)

            # Verificar sidebar responsive
            if css_file.name == "style.css":
                self._check_sidebar_responsive(content)

            # Verificar tablas responsive
            self._check_table_responsive(content, css_file.name)

            # Verificar formularios responsive
            self._check_form_responsive(content, css_file.name)

        except Exception as e:
            self.issues.append(f"Error leyendo {css_file.name}: {str(e)}")

    def _check_media_queries(self, content, filename):
        """Verifica que existan las media queries necesarias"""
        media_queries = re.findall(r"@media\s*\([^)]+\)", content)

        required_breakpoints = [
            "max-width: 576px",
            "max-width: 768px",
            "max-width: 992px",
            "min-width: 992px",
        ]
        found_breakpoints = []

        for mq in media_queries:
            for bp in required_breakpoints:
                if bp in mq:
                    found_breakpoints.append(bp)

        missing_breakpoints = set(required_breakpoints) - set(found_breakpoints)

        if missing_breakpoints:
            self.warnings.append(
                f"{filename}: Faltan media queries para breakpoints: {', '.join(missing_breakpoints)}"
            )

    def _check_sidebar_responsive(self, content):
        """Verifica la configuración responsive del sidebar"""
        # Verificar que el sidebar se oculte en móviles
        mobile_sidebar = re.search(
            r"@media\s*\(\s*max-width:\s*991\.98px\s*\)\s*\{[^}]*\.sidebar\s*\{[^}]*transform:\s*translateX\([^)]+\)",
            content,
            re.DOTALL,
        )
        if not mobile_sidebar:
            self.issues.append(
                "CSS: No se encontró configuración responsive para ocultar sidebar en móviles"
            )
        else:
            # Verificar que use translateX(-100%) para ocultar
            if "translateX(-100%)" not in mobile_sidebar.group(0):
                self.issues.append(
                    "CSS: El sidebar no se oculta correctamente en móviles (debe usar translateX(-100%))"
                )

        # Verificar que el sidebar se muestre en desktop
        desktop_sidebar = re.search(
            r"@media\s*\(\s*min-width:\s*992px\s*\)\s*\{[^}]*\.sidebar\s*\{[^}]*transform:\s*translateX\(0\)",
            content,
            re.DOTALL,
        )
        if not desktop_sidebar:
            self.issues.append(
                "CSS: No se encontró configuración para mostrar sidebar en desktop"
            )

        # Verificar configuración de main-content
        main_content_mobile = re.search(
            r"@media\s*\(\s*max-width:\s*991\.98px\s*\)\s*\{[^}]*\.main-content\s*\{[^}]*margin-left:\s*0",
            content,
            re.DOTALL,
        )
        if not main_content_mobile:
            self.issues.append("CSS: main-content no tiene margin-left: 0 en móviles")

        main_content_desktop = re.search(
            r"@media\s*\(\s*min-width:\s*992px\s*\)\s*\{[^}]*\.main-content\s*\{[^}]*margin-left:\s*250px",
            content,
            re.DOTALL,
        )
        if not main_content_desktop:
            self.issues.append(
                "CSS: main-content no tiene margin-left: 250px en desktop"
            )

    def _check_table_responsive(self, content, filename):
        """Verifica que las tablas sean responsive"""
        # Buscar contenedores table-responsive
        responsive_containers = len(re.findall(r"\.table-responsive", content))

        if responsive_containers == 0:
            self.warnings.append(
                f"{filename}: No se encontraron contenedores table-responsive"
            )

        # Verificar que las tablas tengan overflow-x: auto
        overflow_rules = re.findall(
            r"\.table-responsive\s*\{[^}]*overflow-x:\s*[^;]+", content, re.DOTALL
        )
        if overflow_rules:
            for rule in overflow_rules:
                if "auto" not in rule and "scroll" not in rule:
                    self.warnings.append(
                        f"{filename}: table-responsive no tiene overflow-x adecuado"
                    )

    def _check_form_responsive(self, content, filename):
        """Verifica que los formularios sean responsive"""
        # Verificar que los inputs usen clases de Bootstrap
        form_groups = re.findall(r"\.form-group|\.mb-3", content)
        if len(form_groups) == 0:
            self.warnings.append(
                f"{filename}: No se encontraron grupos de formularios responsive"
            )

    def validate_html_templates(self):
        """Valida las plantillas HTML para responsive design"""
        print("🔍 Validando plantillas HTML...")

        templates_dir = self.project_root / "app" / "templates"

        # Revisar plantilla base
        base_template = templates_dir / "base.html"
        if base_template.exists():
            self._validate_base_template(base_template)

        # Revisar algunas plantillas específicas
        templates_to_check = [
            templates_dir / "dashboard" / "dashboard.html",
            templates_dir / "ordenes" / "index.html",
            templates_dir / "inventario" / "index.html",
        ]

        for template in templates_to_check:
            if template.exists():
                self._validate_template(template)

    def _validate_base_template(self, template_path):
        """Valida la plantilla base"""
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Verificar meta viewport
            if 'name="viewport"' not in content:
                self.issues.append(
                    "base.html: Falta meta viewport para responsive design"
                )

            # Verificar Bootstrap
            if "bootstrap" not in content.lower():
                self.issues.append("base.html: No se encontró referencia a Bootstrap")

            # Verificar sidebar overlay
            if "sidebar-overlay" not in content:
                self.issues.append("base.html: Falta overlay para sidebar en móviles")

            # Verificar navbar toggler
            if "navbar-toggler" not in content:
                self.issues.append("base.html: Falta botón toggler para móviles")

        except Exception as e:
            self.issues.append(f"Error leyendo base.html: {str(e)}")

    def _validate_template(self, template_path):
        """Valida una plantilla específica"""
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Verificar clases responsive de Bootstrap
            responsive_classes = re.findall(r"col-(?:lg|md|sm|xs)-\d+", content)
            if len(responsive_classes) == 0:
                self.warnings.append(
                    f"{template_path.name}: No se encontraron clases responsive de Bootstrap"
                )

            # Verificar contenedores responsive
            if "container-fluid" not in content and "container" not in content:
                self.warnings.append(
                    f"{template_path.name}: No se encontraron contenedores responsive"
                )

        except Exception as e:
            self.issues.append(f"Error leyendo {template_path.name}: {str(e)}")

    def validate_javascript(self):
        """Valida la configuración JavaScript para responsive"""
        print("🔍 Validando JavaScript responsive...")

        js_file = self.project_root / "static" / "js" / "main.js"
        if js_file.exists():
            try:
                with open(js_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Verificar función toggleSidebar
                if "function toggleSidebar" not in content:
                    self.issues.append("main.js: Falta función toggleSidebar")

                # Verificar manejo de overlay
                if "sidebar-overlay" not in content:
                    self.issues.append("main.js: No se maneja el overlay del sidebar")

                # Verificar event listener de resize
                if 'window.addEventListener("resize"' not in content:
                    self.issues.append(
                        "main.js: Falta event listener para redimensionamiento de ventana"
                    )

            except Exception as e:
                self.issues.append(f"Error leyendo main.js: {str(e)}")

    def test_application_running(self):
        """Verifica que la aplicación esté ejecutándose"""
        print("🔍 Verificando que la aplicación esté ejecutándose...")

        try:
            response = requests.get("http://127.0.0.1:5000", timeout=5)
            if response.status_code == 200:
                print("  ✅ Aplicación ejecutándose correctamente")
                return True
            else:
                self.issues.append(
                    f"Aplicación responde con código {response.status_code}"
                )
                return False
        except requests.exceptions.RequestException:
            self.issues.append(
                "Aplicación no está ejecutándose en http://127.0.0.1:5000"
            )
            return False

    def generate_report(self):
        """Genera el reporte final"""
        print("\n" + "=" * 60)
        print("📊 REPORTE DE VALIDACIÓN RESPONSIVE")
        print("=" * 60)

        if not self.issues and not self.warnings:
            print("🎉 ¡Todas las validaciones pasaron exitosamente!")
            print("✅ El diseño responsive está correctamente configurado")
            return True

        if self.issues:
            print(f"❌ Se encontraron {len(self.issues)} problemas críticos:")
            for issue in self.issues:
                print(f"   • {issue}")

        if self.warnings:
            print(f"⚠️  Se encontraron {len(self.warnings)} advertencias:")
            for warning in self.warnings:
                print(f"   • {warning}")

        if self.issues:
            print(
                "\n🔧 Los problemas críticos deben corregirse para asegurar funcionalidad responsive"
            )
            return False
        else:
            print("\n✅ Solo hay advertencias menores - el responsive básico funciona")
            return True


def main():
    print("🧪 Iniciando validación de responsive design para GMAO")
    print("=" * 60)

    # Obtener ruta del proyecto
    script_dir = Path(__file__).parent
    project_root = script_dir

    validator = ResponsiveValidator(project_root)

    # Ejecutar validaciones
    validator.validate_css_responsive()
    validator.validate_html_templates()
    validator.validate_javascript()
    app_running = validator.test_application_running()

    # Generar reporte
    success = validator.generate_report()

    if not app_running:
        print("\n💡 Para probar completamente el responsive design:")
        print("   1. Ejecuta: python run.py")
        print("   2. Abre: http://127.0.0.1:5000")
        print("   3. Prueba redimensionando la ventana del navegador")

    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
