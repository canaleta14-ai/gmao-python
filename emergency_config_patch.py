#!/usr/bin/env python3
"""
Script de emergencia para parchear la configuración de la aplicación en producción
Este script modifica temporalmente la configuración para usar valores hardcoded
"""

import requests
import json


def patch_production_config():
    """Intenta patchear la configuración de producción"""

    # URL de la aplicación en producción
    base_url = "https://mantenimiento-470311.ew.r.appspot.com"

    try:
        # Primero verificamos el estado actual
        print("🔍 Verificando estado actual...")
        health_response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Estado actual: {health_response.status_code}")
        if health_response.status_code == 503:
            print("✗ La aplicación confirma problemas de BD")

        # Intentamos llamar a nuestro endpoint de emergencia
        print("🚨 Intentando activar endpoint de emergencia...")
        emergency_response = requests.post(
            f"{base_url}/admin/emergency-reload-config", timeout=10
        )

        if emergency_response.status_code == 200:
            print("✅ Endpoint de emergencia ejecutado correctamente")
            print(f"Respuesta: {emergency_response.json()}")

            # Verificar si ahora funciona el health check
            print("🔍 Verificando estado después del patch...")
            health_check = requests.get(f"{base_url}/health", timeout=10)
            if health_check.status_code == 200:
                print("✅ ¡La aplicación ahora funciona correctamente!")
                return True
            else:
                print("✗ La aplicación sigue con problemas")

        else:
            print(
                f"✗ Error en endpoint de emergencia: {emergency_response.status_code}"
            )
            if emergency_response.status_code == 404:
                print("   El endpoint no existe (necesita deploy)")

        return False

    except Exception as e:
        print(f"❌ Error en patch: {e}")
        return False


if __name__ == "__main__":
    print("=== PARCHE DE EMERGENCIA PARA CONFIGURACIÓN ===")
    success = patch_production_config()

    if success:
        print("\n🎉 ¡Problema resuelto temporalmente!")
        print("   La aplicación debería funcionar ahora.")
        print("   Recuerda hacer un deploy oficial cuando sea posible.")
    else:
        print("\n❌ No se pudo resolver el problema automáticamente.")
        print("   Necesitas hacer deploy del fix manualmente.")
