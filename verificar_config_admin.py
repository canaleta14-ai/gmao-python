import os
import requests
import json


def verificar_configuracion_admin():
    """
    Verificar la configuración de administradores para emails
    """
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN DE ADMINISTRADORES")
    print("=" * 50)

    base_url = "https://mantenimiento-470311.ew.r.appspot.com"

    # 1. Verificar si hay un endpoint de configuración
    endpoints_config = [
        "/api/admin/usuarios",
        "/admin/usuarios",
        "/api/config",
        "/config",
    ]

    session = requests.Session()

    for endpoint in endpoints_config:
        try:
            url = f"{base_url}{endpoint}"
            print(f"📡 Probando endpoint: {endpoint}")
            response = session.get(url, timeout=10)
            print(f"   📊 Código: {response.status_code}")

            if response.status_code == 200:
                if "json" in response.headers.get("content-type", ""):
                    try:
                        data = response.json()
                        print(f"   📋 Datos encontrados: {type(data)}")
                        if isinstance(data, (list, dict)):
                            print(
                                f"   📧 Información: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}..."
                            )
                    except:
                        pass

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

    print("\n" + "=" * 50)

    # 2. Hacer una solicitud de prueba y verificar que se creó
    print("🧪 VERIFICAR SOLICITUD CREADA EN BD")
    print("=" * 30)

    # Verificar si hay endpoint para verificar solicitudes recientes
    endpoints_solicitudes = [
        "/api/solicitudes/recientes",
        "/admin/solicitudes/api/filtrar",
        "/api/solicitudes",
    ]

    for endpoint in endpoints_solicitudes:
        try:
            url = f"{base_url}{endpoint}"
            print(f"📡 Probando endpoint: {endpoint}")
            response = session.get(url, timeout=10)
            print(f"   📊 Código: {response.status_code}")

            if response.status_code == 200:
                if "json" in response.headers.get("content-type", ""):
                    try:
                        data = response.json()
                        print(f"   📋 Datos encontrados: {type(data)}")

                        # Buscar solicitudes recientes con "Test Email"
                        if isinstance(data, dict):
                            if "data" in data:
                                solicitudes = data["data"]
                            elif "solicitudes" in data:
                                solicitudes = data["solicitudes"]
                            else:
                                solicitudes = [data]
                        elif isinstance(data, list):
                            solicitudes = data
                        else:
                            solicitudes = []

                        # Verificar si alguna solicitud contiene "Test Email"
                        for solicitud in solicitudes[:5]:  # Solo las primeras 5
                            if isinstance(solicitud, dict):
                                nombre = solicitud.get("nombre_solicitante", "")
                                descripcion = solicitud.get(
                                    "descripcion", ""
                                ) or solicitud.get("descripcion_problema", "")
                                numero = solicitud.get("numero_solicitud", "")

                                if "Test Email" in nombre or "PRUEBA EMAIL" in str(
                                    descripcion
                                ):
                                    print(f"   ✅ Solicitud de prueba encontrada:")
                                    print(f"      📝 Número: {numero}")
                                    print(f"      👤 Solicitante: {nombre}")
                                    print(
                                        f"      📋 Descripción: {str(descripcion)[:100]}..."
                                    )
                                    break

                    except Exception as e:
                        print(f"   ❌ Error parseando JSON: {str(e)}")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


if __name__ == "__main__":
    verificar_configuracion_admin()
