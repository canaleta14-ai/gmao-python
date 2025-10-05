#!/usr/bin/env python3
"""
Test para verificar que el fix de usuarios inactivos funciona en producción
"""

import requests
import json
import sys
import time

def test_produccion_usuarios_inactivos():
    """Test para verificar que el fix funciona en la aplicación desplegada"""
    
    base_url = "https://gmao-sistema-2025.ew.r.appspot.com"
    
    print("TEST DE PRODUCCION - Fix Usuarios Inactivos")
    print(f"URL: {base_url}")
    print("=" * 60)
    
    # 1. Verificar que la aplicación responde
    print("1. Verificando que la aplicación responde...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("OK - Aplicación responde correctamente")
        else:
            print(f"WARNING - Aplicación responde con código: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR - Error al conectar con la aplicación: {e}")
        return False
    
    # 2. Login como admin
    print("\n2. Haciendo login como admin...")
    session = requests.Session()
    
    # Obtener página de login
    try:
        login_page = session.get(f"{base_url}/login", timeout=10)
        if login_page.status_code != 200:
            print(f"ERROR - Error al acceder a página de login: {login_page.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"ERROR - Error al acceder a login: {e}")
        return False
    
    # Hacer login
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = session.post(
            f"{base_url}/login", 
            data=login_data, 
            allow_redirects=False,
            timeout=10
        )
        if login_response.status_code not in [200, 302]:
            print(f"ERROR - Error en login: {login_response.status_code}")
            return False
        print("OK - Login exitoso")
    except requests.exceptions.RequestException as e:
        print(f"ERROR - Error durante login: {e}")
        return False
    
    # 3. Obtener lista de usuarios
    print("\n3. Obteniendo lista de usuarios...")
    try:
        usuarios_response = session.get(f"{base_url}/usuarios/api", timeout=15)
        if usuarios_response.status_code != 200:
            print(f"ERROR - Error al obtener usuarios: {usuarios_response.status_code}")
            return False
        
        usuarios_data = usuarios_response.json()
        if not usuarios_data.get("success"):
            print(f"ERROR - Error en respuesta de usuarios: {usuarios_data}")
            return False
        
        usuarios = usuarios_data.get("usuarios", [])
        print(f"OK - Se encontraron {len(usuarios)} usuarios")
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR - Error al obtener usuarios: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR - Error al decodificar respuesta JSON: {e}")
        return False
    
    if not usuarios:
        print("ERROR - No hay usuarios para probar")
        return False
    
    # Buscar un usuario que no sea admin
    usuario_test = None
    for usuario in usuarios:
        if usuario.get("username") != "admin":
            usuario_test = usuario
            break
    
    if not usuario_test:
        print("ERROR - No se encontró usuario para probar (solo admin disponible)")
        return False
    
    print(f"OK - Usuario de prueba: {usuario_test.get('nombre')} ({usuario_test.get('username')})")
    print(f"   Estado actual: {usuario_test.get('estado')}")
    
    # 4. Cambiar usuario a inactivo
    print("\n4. Cambiando usuario a inactivo...")
    nuevo_estado = "Inactivo" if usuario_test.get("estado") == "Activo" else "Activo"
    
    update_data = {
        "username": usuario_test.get("username"),
        "email": usuario_test.get("email"),
        "nombre": usuario_test.get("nombre"),
        "rol": usuario_test.get("rol"),
        "estado": nuevo_estado
    }
    
    try:
        update_response = session.put(
            f"{base_url}/usuarios/api/{usuario_test.get('id')}",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if update_response.status_code != 200:
            print(f"ERROR - Error al actualizar usuario: {update_response.status_code}")
            print(f"   Respuesta: {update_response.text}")
            return False
        
        update_result = update_response.json()
        if not update_result.get("success"):
            print(f"ERROR - Error en actualización: {update_result}")
            return False
        
        print(f"OK - Usuario actualizado a: {nuevo_estado}")
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR - Error durante actualización: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR - Error al decodificar respuesta de actualización: {e}")
        return False
    
    # 5. Esperar un momento para que se propague
    print("\n5. Esperando propagación de cambios...")
    time.sleep(2)
    
    # 6. Verificar que el cambio se reflejó
    print("6. Verificando que el cambio se reflejó...")
    try:
        usuarios_response_2 = session.get(f"{base_url}/usuarios/api", timeout=15)
        if usuarios_response_2.status_code != 200:
            print(f"ERROR - Error al obtener usuarios actualizados: {usuarios_response_2.status_code}")
            return False
        
        usuarios_data_2 = usuarios_response_2.json()
        usuarios_2 = usuarios_data_2.get("usuarios", [])
        
        # Buscar el usuario actualizado
        usuario_actualizado = None
        for usuario in usuarios_2:
            if usuario.get("id") == usuario_test.get("id"):
                usuario_actualizado = usuario
                break
        
        if not usuario_actualizado:
            print("ERROR - No se encontró el usuario actualizado")
            return False
        
        estado_actual = usuario_actualizado.get("estado")
        print(f"   Estado actual en la lista: {estado_actual}")
        
        if estado_actual == nuevo_estado:
            print(f"SUCCESS - El usuario ahora aparece como: {estado_actual}")
            print("SUCCESS - El fix de usuarios inactivos funciona correctamente en producción!")
            return True
        else:
            print(f"FAIL - El usuario debería aparecer como '{nuevo_estado}' pero aparece como '{estado_actual}'")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR - Error al verificar cambios: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR - Error al decodificar respuesta de verificación: {e}")
        return False

if __name__ == "__main__":
    try:
        success = test_produccion_usuarios_inactivos()
        print("\n" + "=" * 60)
        if success:
            print("SUCCESS - TEST COMPLETADO EXITOSAMENTE!")
            print("OK - El fix de usuarios inactivos está funcionando en producción")
            sys.exit(0)
        else:
            print("FAIL - TEST FALLÓ!")
            print("ERROR - El fix no está funcionando correctamente en producción")
            sys.exit(1)
    except Exception as e:
        print(f"\nERROR - Error durante el test: {e}")
        sys.exit(1)
