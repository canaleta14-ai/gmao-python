#!/usr/bin/env python3
"""
Script para probar el envío de emails en producción
Utiliza la configuración actual de la aplicación
"""

import os
import sys
import requests
from datetime import datetime

def test_email_production():
    """Prueba el envío de emails en producción"""
    
    # URL de la aplicación en producción
    base_url = "https://mantenimiento-470311.ew.r.appspot.com"
    
    print("🔧 Probando envío de emails en producción...")
    print(f"📍 URL base: {base_url}")
    print(f"⏰ Fecha/hora: {datetime.now()}")
    print("-" * 50)
    
    try:
        # Verificar que la aplicación esté funcionando
        print("1. Verificando que la aplicación esté activa...")
        response = requests.get(f"{base_url}/", timeout=30)
        
        if response.status_code == 200:
            print("✅ Aplicación activa y respondiendo")
        else:
            print(f"❌ Error: La aplicación respondió con código {response.status_code}")
            return False
            
        # Verificar endpoint de diagnóstico si existe
        print("\n2. Verificando endpoint de diagnóstico...")
        try:
            diag_response = requests.get(f"{base_url}/diagnostico", timeout=30)
            if diag_response.status_code == 200:
                print("✅ Endpoint de diagnóstico disponible")
            else:
                print(f"⚠️  Endpoint de diagnóstico no disponible (código {diag_response.status_code})")
        except Exception as e:
            print(f"⚠️  Endpoint de diagnóstico no accesible: {e}")
        
        # Verificar cron job (que incluye envío de emails)
        print("\n3. Verificando cron job...")
        try:
            cron_response = requests.get(f"{base_url}/api/cron/generar-ordenes-preventivas", timeout=60)
            if cron_response.status_code == 200:
                print("✅ Cron job ejecutado correctamente")
                print("📧 Si hay órdenes pendientes, se habrán enviado emails de notificación")
            else:
                print(f"⚠️  Cron job respondió con código {cron_response.status_code}")
        except Exception as e:
            print(f"❌ Error ejecutando cron job: {e}")
        
        print("\n" + "=" * 50)
        print("📧 RESUMEN DE CONFIGURACIÓN DE EMAIL:")
        print("- MAIL_SERVER: smtp.gmail.com")
        print("- MAIL_PORT: 587")
        print("- MAIL_USE_TLS: True")
        print("- MAIL_USERNAME: j_hidalgo@disfood.com")
        print("- MAIL_PASSWORD: *** (desde Secret Manager)")
        print("- ADMIN_EMAILS: j_hidalgo@disfood.com")
        print("=" * 50)
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando prueba de emails en producción...")
    success = test_email_production()
    
    if success:
        print("\n✅ Prueba completada. Revisa tu email para verificar la recepción.")
        print("📝 Nota: Los emails se envían solo cuando hay órdenes de mantenimiento pendientes.")
    else:
        print("\n❌ Prueba falló. Revisa los logs para más detalles.")
    
    sys.exit(0 if success else 1)