#!/usr/bin/env python3
"""
Test para verificar que el cambio de estado de usuario a inactivo funciona correctamente
"""

import requests
import json
import sys

def test_usuario_inactivo():
    """Test para verificar que un usuario marcado como inactivo aparece correctamente"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Iniciando test de usuario inactivo...")
    
    # 1. Login como admin
    print("1. Haciendo login como admin...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    session = requests.Session()
    
    # Obtener página de login primero
    login_page = session.get(f"{base_url}/login")
    if login_page.status_code != 200:
        print(f"❌ Error al acceder a página de login: {login_page.status_code}")
        return False
    
    # Hacer login
    login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    if login_response.status_code not in [200, 302]:
        print(f"❌ Error en login: {login_response.status_code}")
        return False
    
    print("✅ Login exitoso")
    
    # 2. Obtener lista de usuarios
    print("2. Obteniendo lista de usuarios...")
    usuarios_response = session.get(f"{base_url}/usuarios/api")
    if usuarios_response.status_code != 200:
        print(f"❌ Error al obtener usuarios: {usuarios_response.status_code}")
        return False
    
    usuarios_data = usuarios_response.json()
    if not usuarios_data.get("success"):
        print(f"❌ Error en respuesta de usuarios: {usuarios_data}")
        return False
    
    usuarios = usuarios_data.get("usuarios", [])
    print(f"✅ Se encontraron {len(usuarios)} usuarios")
    
    if not usuarios:
        print("❌ No hay usuarios para probar")
        return False
    
    # Buscar un usuario que no sea admin
    usuario_test = None
    for usuario in usuarios:
        if usuario.get("username") != "admin":
            usuario_test = usuario
            break
    
    if not usuario_test:
        print("❌ No se encontró usuario para probar (solo admin disponible)")
        return False
    
    print(f"✅ Usuario de prueba: {usuario_test.get('nombre')} ({usuario_test.get('username')})")
    print(f"   Estado actual: {usuario_test.get('estado')}")
    
    # 3. Cambiar usuario a inactivo
    print("3. Cambiando usuario a inactivo...")
    nuevo_estado = "Inactivo" if usuario_test.get("estado") == "Activo" else "Activo"
    
    update_data = {
        "username": usuario_test.get("username"),
        "email": usuario_test.get("email"),
        "nombre": usuario_test.get("nombre"),
        "rol": usuario_test.get("rol"),
        "estado": nuevo_estado
    }
    
    update_response = session.put(
        f"{base_url}/usuarios/api/{usuario_test.get('id')}",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    if update_response.status_code != 200:
        print(f"❌ Error al actualizar usuario: {update_response.status_code}")
        print(f"   Respuesta: {update_response.text}")
        return False
    
    update_result = update_response.json()
    if not update_result.get("success"):
        print(f"❌ Error en actualización: {update_result}")
        return False
    
    print(f"✅ Usuario actualizado a: {nuevo_estado}")
    
    # 4. Verificar que el cambio se reflejó
    print("4. Verificando que el cambio se reflejó...")
    usuarios_response_2 = session.get(f"{base_url}/usuarios/api")
    if usuarios_response_2.status_code != 200:
        print(f"❌ Error al obtener usuarios actualizados: {usuarios_response_2.status_code}")
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
        print("❌ No se encontró el usuario actualizado")
        return False
    
    estado_actual = usuario_actualizado.get("estado")
    print(f"   Estado actual en la lista: {estado_actual}")
    
    if estado_actual == nuevo_estado:
        print(f"✅ ¡ÉXITO! El usuario ahora aparece como: {estado_actual}")
        return True
    else:
        print(f"❌ FALLO: El usuario debería aparecer como '{nuevo_estado}' pero aparece como '{estado_actual}'")
        return False

if __name__ == "__main__":
    try:
        success = test_usuario_inactivo()
        if success:
            print("\n🎉 Test completado exitosamente!")
            sys.exit(0)
        else:
            print("\n💥 Test falló!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error durante el test: {e}")
        sys.exit(1)


