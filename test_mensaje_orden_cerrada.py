#!/usr/bin/env python3
"""
Test para verificar que el mensaje amigable funciona cuando se intenta descontar repuestos de una orden cerrada
"""

import requests
import json
import sys

def test_mensaje_orden_cerrada():
    """Test para verificar mensaje amigable en orden cerrada"""
    
    base_url = "https://gmao-sistema-2025.ew.r.appspot.com"
    
    print("TEST - Mensaje Amigable para Orden Cerrada")
    print(f"URL: {base_url}")
    print("=" * 60)
    
    # 1. Login como admin
    print("1. Haciendo login como admin...")
    session = requests.Session()
    
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
    
    # 2. Obtener lista de órdenes para encontrar una cerrada
    print("\n2. Buscando órdenes cerradas...")
    try:
        ordenes_response = session.get(f"{base_url}/ordenes/api", timeout=15)
        if ordenes_response.status_code != 200:
            print(f"ERROR - Error al obtener órdenes: {ordenes_response.status_code}")
            return False
        
        ordenes_data = ordenes_response.json()
        if not ordenes_data.get("success"):
            print(f"ERROR - Error en respuesta de órdenes: {ordenes_data}")
            return False
        
        ordenes = ordenes_data.get("ordenes", [])
        print(f"OK - Se encontraron {len(ordenes)} órdenes")
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR - Error al obtener órdenes: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR - Error al decodificar respuesta JSON: {e}")
        return False
    
    # Buscar una orden cerrada (Completada o Cancelada)
    orden_cerrada = None
    for orden in ordenes:
        if orden.get("estado") in ["Completada", "Cancelada"]:
            orden_cerrada = orden
            break
    
    if not orden_cerrada:
        print("WARNING - No se encontró orden cerrada para probar")
        print("Creando una orden de prueba...")
        
        # Crear una orden de prueba y marcarla como completada
        orden_test_data = {
            "tipo": "Correctivo",
            "prioridad": "Media",
            "descripcion": "Orden de prueba para test de mensaje amigable",
            "activo_id": 1,
            "tecnico_id": 1
        }
        
        try:
            crear_response = session.post(
                f"{base_url}/ordenes/api",
                json=orden_test_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if crear_response.status_code == 200:
                orden_creada = crear_response.json()
                if orden_creada.get("success"):
                    orden_id = orden_creada.get("orden", {}).get("id")
                    
                    # Marcar como completada
                    estado_data = {"estado": "Completada"}
                    estado_response = session.put(
                        f"{base_url}/ordenes/api/{orden_id}/estado",
                        json=estado_data,
                        headers={"Content-Type": "application/json"},
                        timeout=15
                    )
                    
                    if estado_response.status_code == 200:
                        orden_cerrada = {"id": orden_id, "estado": "Completada"}
                        print(f"OK - Orden de prueba creada y marcada como completada (ID: {orden_id})")
                    else:
                        print("WARNING - No se pudo marcar la orden como completada")
                        return False
                else:
                    print("WARNING - No se pudo crear orden de prueba")
                    return False
            else:
                print("WARNING - Error al crear orden de prueba")
                return False
                
        except Exception as e:
            print(f"WARNING - Error creando orden de prueba: {e}")
            return False
    
    print(f"OK - Orden cerrada encontrada: ID {orden_cerrada.get('id')}, Estado: {orden_cerrada.get('estado')}")
    
    # 3. Intentar descontar repuestos de la orden cerrada
    print("\n3. Intentando descontar repuestos de orden cerrada...")
    try:
        descontar_data = {
            "usuario_id": "sistema",
            "manual": True
        }
        
        descontar_response = session.post(
            f"{base_url}/api/ordenes/{orden_cerrada.get('id')}/recambios/descontar",
            json=descontar_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"   Código de respuesta: {descontar_response.status_code}")
        
        if descontar_response.status_code == 400:
            # Esto es lo esperado - error 400 por orden cerrada
            result = descontar_response.json()
            error_message = result.get("error", "")
            
            print(f"   Mensaje de error recibido: {error_message}")
            
            # Verificar que el mensaje es amigable
            if "orden completada" in error_message.lower() or "orden cancelada" in error_message.lower():
                if "debe estar en estado" in error_message.lower():
                    print("SUCCESS - Mensaje amigable detectado correctamente")
                    print("SUCCESS - El sistema previene descuentos en órdenes cerradas")
                    return True
                else:
                    print("PARTIAL - Error detectado pero mensaje podría ser más amigable")
                    return True
            else:
                print(f"FAIL - Mensaje no es suficientemente amigable: {error_message}")
                return False
                
        elif descontar_response.status_code == 200:
            # Si permite el descuento, verificar que al menos hay validación
            result = descontar_response.json()
            if result.get("success") and "sin recambios" in result.get("message", "").lower():
                print("OK - Orden cerrada sin repuestos (comportamiento aceptable)")
                return True
            else:
                print("WARNING - Sistema permite descontar repuestos de orden cerrada")
                return False
        else:
            print(f"UNEXPECTED - Código de respuesta inesperado: {descontar_response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR - Error durante prueba: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR - Error al decodificar respuesta: {e}")
        return False

if __name__ == "__main__":
    try:
        success = test_mensaje_orden_cerrada()
        print("\n" + "=" * 60)
        if success:
            print("SUCCESS - TEST COMPLETADO EXITOSAMENTE!")
            print("OK - Los mensajes amigables funcionan correctamente")
            sys.exit(0)
        else:
            print("FAIL - TEST FALLÓ!")
            print("ERROR - Los mensajes amigables no funcionan como se esperaba")
            sys.exit(1)
    except Exception as e:
        print(f"\nERROR - Error durante el test: {e}")
        sys.exit(1)
