#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def init_production_database():
    """Inicializar base de datos de producción via HTTP"""
    
    base_url = "https://mantenimiento-470311.ew.r.appspot.com"
    
    print("=== INICIALIZACIÓN DE BASE DE DATOS DE PRODUCCIÓN ===\n")
    
    print(f"🌐 Conectando a aplicación en producción: {base_url}")
    
    # 1. Verificar que la aplicación esté funcionando
    try:
        response = requests.get(f"{base_url}/", timeout=30)
        if response.status_code == 200:
            print("   ✅ Aplicación en producción está funcionando")
        else:
            print(f"   ⚠️ Aplicación responde con código: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error conectando a aplicación: {e}")
        return False
    
    # 2. Intentar acceder al endpoint de inicialización de DB
    print("\n🗄️ Inicializando base de datos...")
    try:
        # Usar el endpoint de diagnóstico para inicializar DB
        response = requests.get(f"{base_url}/diagnostico/db-init", timeout=60)
        if response.status_code == 200:
            print("   ✅ Base de datos inicializada correctamente")
        else:
            print(f"   ⚠️ Respuesta del endpoint de inicialización: {response.status_code}")
            print(f"   Contenido: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error inicializando base de datos: {e}")
    
    # 3. Crear usuario administrador via endpoint
    print("\n👤 Creando usuario administrador...")
    try:
        # Datos del usuario administrador
        admin_data = {
            "username": "admin",
            "email": "admin@gmao.com",
            "password": "admin123",
            "nombre": "Administrador Sistema",
            "rol": "Administrador"
        }
        
        # Intentar crear usuario via endpoint de registro
        response = requests.post(
            f"{base_url}/api/usuarios/crear-admin",
            json=admin_data,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code in [200, 201]:
            print("   ✅ Usuario administrador creado exitosamente")
        else:
            print(f"   ⚠️ Respuesta del endpoint de usuario: {response.status_code}")
            print(f"   Contenido: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Error creando usuario administrador: {e}")
    
    # 4. Verificar estado de la aplicación
    print("\n📊 Verificando estado de la aplicación...")
    try:
        response = requests.get(f"{base_url}/diagnostico/estado", timeout=30)
        if response.status_code == 200:
            print("   ✅ Diagnóstico de estado exitoso")
            # Intentar mostrar información del estado si está disponible
            try:
                estado = response.json()
                print(f"   📈 Estado: {estado}")
            except:
                print(f"   📄 Respuesta: {response.text[:200]}...")
        else:
            print(f"   ⚠️ Estado del diagnóstico: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error verificando estado: {e}")
    
    print("\n✅ Proceso de inicialización completado.")
    print("\n🌐 Aplicación disponible en:")
    print(f"   {base_url}")
    print(f"   {base_url}/login")
    print("\n🔐 Credenciales de administrador:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("\n🚨 IMPORTANTE: Cambiar la contraseña inmediatamente después del primer login")
    
    return True

if __name__ == "__main__":
    try:
        success = init_production_database()
        if success:
            print("\n🎉 Inicialización completada.")
        else:
            print("\n❌ Error en la inicialización.")
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        import traceback
        traceback.print_exc()