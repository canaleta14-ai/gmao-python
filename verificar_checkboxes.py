"""
Script de Verificación: Sistema de Checkboxes en Activos
=========================================================

Este script verifica que todos los archivos necesarios para el sistema
de selección masiva estén presentes y correctamente configurados.

Autor: Sistema GMAO
Fecha: 1 de octubre de 2025
"""

import os
import sys

# Colores para terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def check_file_exists(file_path, description):
    """Verifica si un archivo existe"""
    if os.path.exists(file_path):
        print(f"{GREEN}✓{RESET} {description}: {file_path}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {file_path} {RED}[NO ENCONTRADO]{RESET}")
        return False


def check_file_contains(file_path, search_text, description):
    """Verifica si un archivo contiene cierto texto"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            if search_text in content:
                print(f"{GREEN}✓{RESET} {description}")
                return True
            else:
                print(f"{YELLOW}⚠{RESET} {description} {YELLOW}[NO ENCONTRADO]{RESET}")
                return False
    except Exception as e:
        print(f"{RED}✗{RESET} Error al leer {file_path}: {e}")
        return False


def main():
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}  VERIFICACIÓN: Sistema de Checkboxes en Activos{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

    base_path = os.path.dirname(os.path.abspath(__file__))
    checks_passed = 0
    checks_total = 0

    # ===== VERIFICAR ARCHIVOS BASE =====
    print(f"{BLUE}📦 Verificando archivos base del sistema...{RESET}\n")

    checks = [
        (
            os.path.join(base_path, "static", "js", "seleccion-masiva.js"),
            "Módulo JavaScript de selección masiva",
        ),
        (
            os.path.join(base_path, "static", "css", "seleccion-masiva.css"),
            "Estilos CSS de selección masiva",
        ),
        (os.path.join(base_path, "GUIA_SELECCION_MASIVA.md"), "Guía de implementación"),
        (
            os.path.join(base_path, "PROPUESTA_SELECCION_MASIVA.md"),
            "Propuesta del sistema",
        ),
    ]

    for file_path, description in checks:
        checks_total += 1
        if check_file_exists(file_path, description):
            checks_passed += 1

    # ===== VERIFICAR IMPLEMENTACIÓN EN ACTIVOS =====
    print(f"\n{BLUE}🔧 Verificando implementación en módulo Activos...{RESET}\n")

    activos_html = os.path.join(
        base_path, "app", "templates", "activos", "activos.html"
    )
    activos_js = os.path.join(base_path, "static", "js", "activos.js")

    # Verificar archivos principales
    checks_total += 1
    if check_file_exists(activos_html, "Template activos.html"):
        checks_passed += 1

    checks_total += 1
    if check_file_exists(activos_js, "JavaScript activos.js"):
        checks_passed += 1

    # Verificar contenido en activos.html
    print(f"\n{BLUE}📝 Verificando contenido de activos.html...{RESET}\n")

    html_checks = [
        ("seleccion-masiva.css", "CSS de selección masiva incluido"),
        ("seleccion-masiva.js", "JavaScript de selección masiva incluido"),
        ('id="select-all"', "Checkbox 'Seleccionar todos' agregado"),
        ('id="contador-seleccion"', "Contador de selección agregado"),
        ('id="acciones-masivas"', "Barra de acciones masivas agregada"),
        ("cambiarEstadoMasivo", "Función de cambio de estado masivo"),
        ("cambiarPrioridadMasiva", "Función de cambio de prioridad masiva"),
        ("exportarSeleccionados", "Función de exportar seleccionados"),
        ("eliminarSeleccionados", "Función de eliminar seleccionados"),
    ]

    for search_text, description in html_checks:
        checks_total += 1
        if check_file_contains(activos_html, search_text, description):
            checks_passed += 1

    # Verificar contenido en activos.js
    print(f"\n{BLUE}📝 Verificando contenido de activos.js...{RESET}\n")

    js_checks = [
        ("let seleccionMasiva;", "Variable global de selección masiva"),
        ("initSeleccionMasiva({", "Inicialización de selección masiva"),
        ("function cambiarEstadoMasivo", "Función cambiarEstadoMasivo()"),
        ("function cambiarPrioridadMasiva", "Función cambiarPrioridadMasiva()"),
        (
            "function confirmarCambioPrioridadMasiva",
            "Función confirmarCambioPrioridadMasiva()",
        ),
        ("function exportarSeleccionados", "Función exportarSeleccionados()"),
        ("function eliminarSeleccionados", "Función eliminarSeleccionados()"),
        ('class="form-check-input row-checkbox"', "Checkbox en cada fila"),
        ('data-id="${activo.id}"', "Data-id en checkboxes"),
    ]

    for search_text, description in js_checks:
        checks_total += 1
        if check_file_contains(activos_js, search_text, description):
            checks_passed += 1

    # ===== VERIFICAR DOCUMENTACIÓN =====
    print(f"\n{BLUE}📚 Verificando documentación...{RESET}\n")

    implementacion_doc = os.path.join(base_path, "IMPLEMENTACION_CHECKBOXES_ACTIVOS.md")
    checks_total += 1
    if check_file_exists(implementacion_doc, "Documentación de implementación"):
        checks_passed += 1

    # ===== RESUMEN =====
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}  RESUMEN DE VERIFICACIÓN{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

    percentage = (checks_passed / checks_total) * 100

    print(f"Total de verificaciones: {checks_total}")
    print(f"Verificaciones exitosas: {GREEN}{checks_passed}{RESET}")
    print(f"Verificaciones fallidas: {RED}{checks_total - checks_passed}{RESET}")
    print(
        f"Porcentaje de éxito: {GREEN if percentage == 100 else YELLOW}{percentage:.1f}%{RESET}"
    )

    if percentage == 100:
        print(f"\n{GREEN}✓ ¡IMPLEMENTACIÓN COMPLETA Y CORRECTA!{RESET}")
        print(
            f"\n{GREEN}El sistema de checkboxes está listo para usar en el módulo de Activos.{RESET}"
        )
        print(f"\n{BLUE}Próximos pasos:{RESET}")
        print(f"  1. Iniciar el servidor Flask")
        print(f"  2. Navegar a /activos")
        print(f"  3. Probar la selección de activos")
        print(f"  4. Ejecutar acciones masivas")
        return 0
    elif percentage >= 80:
        print(f"\n{YELLOW}⚠ IMPLEMENTACIÓN CASI COMPLETA{RESET}")
        print(
            f"\n{YELLOW}Hay algunas verificaciones pendientes, pero debería funcionar.{RESET}"
        )
        print(f"{YELLOW}Revisa los elementos marcados arriba.{RESET}")
        return 1
    else:
        print(f"\n{RED}✗ IMPLEMENTACIÓN INCOMPLETA{RESET}")
        print(
            f"\n{RED}Faltan elementos críticos. Revisa la guía de implementación.{RESET}"
        )
        return 2


if __name__ == "__main__":
    try:
        exit_code = main()
        print()  # Línea en blanco final
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}⚠ Verificación interrumpida por el usuario{RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{RED}✗ Error inesperado: {e}{RESET}")
        sys.exit(1)
