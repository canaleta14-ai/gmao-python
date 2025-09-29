#!/usr/bin/env python3
"""
Script simple para probar el responsive design de la aplicación GMAO
Abre el navegador y permite probar diferentes tamaños de pantalla
"""

import webbrowser
import time
import requests
import subprocess
import sys
import os


def check_app_running():
    """Verifica si la aplicación está ejecutándose"""
    try:
        response = requests.get("http://127.0.0.1:5000", timeout=5)
        return response.status_code == 200
    except:
        return False


def open_browser_with_sizes():
    """Abre el navegador con diferentes tamaños simulados"""
    print("🖥️  Probando responsive design de GMAO")
    print("=" * 50)

    if not check_app_running():
        print("❌ La aplicación no está ejecutándose.")
        print("💡 Ejecuta primero: python run.py")
        return False

    print("✅ Aplicación ejecutándose en http://127.0.0.1:5000")

    # Abrir navegador
    url = "http://127.0.0.1:5000"
    print(f"🌐 Abriendo navegador en: {url}")
    webbrowser.open(url)

    print("\n📱 INSTRUCCIONES PARA PROBAR RESPONSIVE DESIGN:")
    print("=" * 50)
    print("1. 📺 Desktop Grande (>1200px):")
    print("   - Sidebar debe estar visible a la izquierda")
    print("   - Contenido principal debe tener margen izquierdo")
    print("   - Navbar hamburguesa debe estar oculta")
    print()
    print("2. 💻 Desktop Mediano (992px-1199px):")
    print("   - Sidebar debe estar visible")
    print("   - Layout debe adaptarse al ancho disponible")
    print()
    print("3. 📱 Tablet (768px-991px):")
    print("   - Sidebar debe estar OCULTO por defecto")
    print("   - Navbar hamburguesa debe estar VISIBLE")
    print("   - Al hacer clic en hamburguesa, sidebar debe aparecer")
    print("   - Debe haber overlay oscuro al abrir sidebar")
    print()
    print("4. 📱 Móvil (320px-767px):")
    print("   - Sidebar completamente OCULTO")
    print("   - Navbar hamburguesa VISIBLE")
    print("   - Contenido debe ocupar todo el ancho")
    print("   - Tablas deben ser scrollables horizontalmente")
    print("   - Formularios deben adaptarse al ancho")
    print()
    print("🔧 HERRAMIENTAS DEL DESARROLLADOR:")
    print("   - Presiona F12 para abrir DevTools")
    print("   - Usa 'Toggle device toolbar' para simular dispositivos")
    print("   - Prueba diferentes breakpoints: 320px, 576px, 768px, 992px, 1200px")
    print()
    print("✅ ELEMENTOS A VERIFICAR:")
    print("   - Sidebar colapsable en móviles")
    print("   - Tablas responsive con scroll horizontal")
    print("   - Formularios que no se desbordan")
    print("   - Texto legible en todos los tamaños")
    print("   - Botones accesibles con dedos")
    print("   - Imágenes que se escalan correctamente")
    print()
    print("🎯 Si encuentras problemas:")
    print("   - Verifica que las media queries estén funcionando")
    print("   - Revisa que Bootstrap esté cargado correctamente")
    print("   - Confirma que el viewport meta tag esté presente")

    return True


def show_css_checklist():
    """Muestra una checklist de verificación CSS"""
    print("\n📋 CHECKLIST DE VERIFICACIÓN CSS:")
    print("=" * 50)
    print("✅ Sidebar oculto en móviles (transform: translateX(-100%))")
    print("✅ Sidebar visible en desktop (transform: translateX(0))")
    print("✅ main-content sin margen en móviles (margin-left: 0)")
    print("✅ main-content con margen en desktop (margin-left: 250px)")
    print("✅ Overlay para cerrar sidebar en móviles")
    print("✅ Tablas con contenedores .table-responsive")
    print("✅ Formularios usando clases Bootstrap (col-*, mb-3, etc.)")
    print("✅ Media queries para breakpoints: 576px, 768px, 992px")
    print("✅ Navbar toggler visible solo en móviles/tablet")
    print("✅ Transiciones suaves para cambios de layout")


def show_js_checklist():
    """Muestra una checklist de verificación JavaScript"""
    print("\n📋 CHECKLIST DE VERIFICACIÓN JAVASCRIPT:")
    print("=" * 50)
    print("✅ Función toggleSidebar() implementada")
    print("✅ Event listener para redimensionamiento de ventana")
    print("✅ Overlay que se muestra/oculta correctamente")
    print("✅ Body scroll bloqueado cuando sidebar está abierto en móviles")
    print("✅ Sidebar se cierra automáticamente al cambiar tamaño de pantalla")


def main():
    print("🧪 HERRAMIENTA DE PRUEBA RESPONSIVE PARA GMAO")
    print("=" * 60)

    # Mostrar checklists
    show_css_checklist()
    show_js_checklist()

    print("\n🚀 Iniciando pruebas...")

    # Verificar aplicación
    if not open_browser_with_sizes():
        sys.exit(1)

    print("\n⏳ Esperando 3 segundos para que se abra el navegador...")
    time.sleep(3)

    print("\n✅ ¡Listo para probar!")
    print("🔄 Redimensiona la ventana del navegador y verifica cada breakpoint")
    print("📝 Anota cualquier problema que encuentres para corregirlo")

    # Mantener el script ejecutándose
    try:
        input("\n⏹️  Presiona Enter para salir...")
    except KeyboardInterrupt:
        pass

    print("👋 ¡Gracias por probar el responsive design!")


if __name__ == "__main__":
    main()
