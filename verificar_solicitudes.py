#!/usr/bin/env python3
"""
Script para verificar las solicitudes en la base de datos
mediante una consulta directa a la API de la aplicación
"""

import requests
import json
from datetime import datetime

# URL base de la aplicación en producción
BASE_URL = "https://mantenimiento-470311.ew.r.appspot.com"


def verificar_solicitudes():
    """Verificar las solicitudes existentes en la base de datos"""

    try:
        print("🔍 Verificando solicitudes en la base de datos...")
        print(f"🌐 URL: {BASE_URL}")
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Intentar acceder a la API de solicitudes
        response = requests.get(
            f"{BASE_URL}/admin/solicitudes/api/filtrar",
            params={
                "estado": "",
                "prioridad": "",
                "tipo_servicio": "",
                "busqueda": "",
                "page": 1,
            },
            timeout=30,
        )

        print(f"📝 Código de respuesta: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            solicitudes = data.get("solicitudes", [])
            total = data.get("total", 0)

            print(f"✅ Respuesta exitosa")
            print(f"📊 Total de solicitudes: {total}")
            print()

            if solicitudes:
                print("📋 Solicitudes encontradas:")
                print("-" * 80)
                for i, sol in enumerate(solicitudes, 1):
                    print(f"{i}. ID: {sol.get('id', 'N/A')}")
                    print(f"   Código: {sol.get('codigo', 'N/A')}")
                    print(f"   Tipo: {sol.get('tipo', 'N/A')}")
                    print(f"   Estado: {sol.get('estado', 'N/A')}")
                    print(f"   Prioridad: {sol.get('prioridad', 'N/A')}")
                    print(f"   Descripción: {sol.get('descripcion', 'N/A')[:50]}...")
                    print(f"   Solicitante: {sol.get('solicitante', 'N/A')}")
                    print(f"   Email: {sol.get('email_solicitante', 'N/A')}")
                    print(f"   Fecha: {sol.get('fecha_creacion', 'N/A')}")
                    print(f"   Ubicación: {sol.get('ubicacion', 'N/A')}")
                    print("-" * 80)
            else:
                print("⚠️  No se encontraron solicitudes")

        elif response.status_code == 401:
            print("🔐 Error 401: No autorizado - se requiere login")
            print(
                "💡 Las solicitudes pueden estar ahí, pero necesitas estar logueado para verlas"
            )
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📋 Respuesta: {response.text[:200]}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear JSON: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


def verificar_solicitudes_publico():
    """Verificar solicitudes sin autenticación"""

    try:
        print("\n🔍 Verificando página pública de solicitudes...")

        response = requests.get(f"{BASE_URL}/solicitudes", timeout=30)

        print(f"📝 Código de respuesta: {response.status_code}")

        if response.status_code == 200:
            # Buscar patrones en el HTML que indiquen solicitudes
            html = response.text

            if "SOL-2025-" in html:
                import re

                solicitudes = re.findall(r"SOL-2025-\d+", html)
                solicitudes_unicas = list(set(solicitudes))

                print(
                    f"✅ Encontradas {len(solicitudes_unicas)} referencias a solicitudes:"
                )
                for sol in solicitudes_unicas:
                    print(f"   - {sol}")
            else:
                print("⚠️  No se encontraron referencias a solicitudes SOL-2025-*")

            if "No hay solicitudes" in html or "tabla vacía" in html:
                print("📋 La página indica que no hay solicitudes")

        else:
            print(f"❌ Error accediendo a solicitudes públicas: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")


def resumen_configuracion():
    """Mostrar resumen de la configuración actual"""
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE CONFIGURACIÓN")
    print("=" * 60)
    print("🌐 URL de producción: https://mantenimiento-470311.ew.r.appspot.com")
    print("🗃️  Base de datos: PostgreSQL Cloud SQL (gmao-madrid-final)")
    print("📧 Email configurado: j_hidalgo@gmail.com")
    print("🔐 Secret: gmao-mail-password (configurado)")
    print("📱 Versión activa: email-fix-v3")
    print()
    print("🔍 Las solicitudes creadas manualmente aparecen en la interfaz.")
    print("🤖 Las solicitudes de prueba automáticas NO aparecen.")
    print("❓ Necesitamos verificar si las automáticas se guardaron en la BD.")


if __name__ == "__main__":
    resumen_configuracion()
    verificar_solicitudes()
    verificar_solicitudes_publico()
