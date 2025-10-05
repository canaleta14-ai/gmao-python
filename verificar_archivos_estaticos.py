#!/usr/bin/env python3
"""
Script para verificar que los archivos estáticos se hayan desplegado correctamente.
"""

import requests
import time

def verificar_archivos_estaticos():
    """Verificar que los archivos JavaScript y CSS estén actualizados"""
    base_url = "https://gmao-sistema-2025.ew.r.appspot.com"
    
    print("🔍 Verificando archivos estáticos en producción...\n")
    
    # Verificar archivo JavaScript de órdenes
    try:
        print("1. Verificando ordenes.js...")
        js_response = requests.get(f"{base_url}/static/js/ordenes.js", timeout=10)
        
        if js_response.status_code == 200:
            print("   ✅ Archivo ordenes.js accesible")
            
            # Verificar funciones de eliminación
            if "mostrarModalEliminarOrden" in js_response.text:
                print("   ✅ Función mostrarModalEliminarOrden encontrada")
            else:
                print("   ❌ Función mostrarModalEliminarOrden NO encontrada")
            
            if "confirmarEliminarOrden" in js_response.text:
                print("   ✅ Función confirmarEliminarOrden encontrada")
            else:
                print("   ❌ Función confirmarEliminarOrden NO encontrada")
                
            # Verificar botón de eliminar en el código
            if 'btn-outline-danger action-btn delete' in js_response.text:
                print("   ✅ Botón de eliminar encontrado en el código")
            else:
                print("   ❌ Botón de eliminar NO encontrado en el código")
                
        else:
            print(f"   ❌ Error accediendo a ordenes.js: {js_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error verificando ordenes.js: {str(e)}")
    
    print()
    
    # Verificar página de órdenes con autenticación simulada
    try:
        print("2. Verificando página de órdenes...")
        
        # Crear una sesión para mantener cookies
        session = requests.Session()
        
        # Intentar acceder a la página principal primero
        main_response = session.get(base_url, timeout=10)
        print(f"   Respuesta página principal: {main_response.status_code}")
        
        # Intentar acceder a órdenes
        ordenes_response = session.get(f"{base_url}/ordenes", timeout=10, allow_redirects=True)
        print(f"   Respuesta página órdenes: {ordenes_response.status_code}")
        
        if ordenes_response.status_code == 200:
            # Verificar modal de eliminación
            if "modalEliminarOrden" in ordenes_response.text:
                print("   ✅ Modal de eliminación encontrado")
            else:
                print("   ❌ Modal de eliminación NO encontrado")
                
            # Verificar script de órdenes
            if "ordenes.js" in ordenes_response.text:
                print("   ✅ Script ordenes.js referenciado")
            else:
                print("   ❌ Script ordenes.js NO referenciado")
        
    except Exception as e:
        print(f"   ❌ Error verificando página de órdenes: {str(e)}")

def main():
    print("=== VERIFICACIÓN DE ARCHIVOS ESTÁTICOS ===\n")
    
    # Esperar un poco para que el despliegue se propague
    print("⏳ Esperando 10 segundos para que el despliegue se propague...")
    time.sleep(10)
    
    verificar_archivos_estaticos()
    
    print("\n=== VERIFICACIÓN COMPLETADA ===")
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Si los archivos estáticos están correctos, el problema puede ser de cache del navegador")
    print("2. Intenta abrir la aplicación en modo incógnito o limpia el cache")
    print("3. URL de la aplicación: https://gmao-sistema-2025.ew.r.appspot.com/ordenes")

if __name__ == "__main__":
    main()