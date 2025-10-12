import requests
import json


def verificar_email_directo():
    """
    Verificar directamente el endpoint de test de email
    """
    print("🔍 VERIFICACIÓN DIRECTA DE EMAIL")
    print("=" * 40)

    base_url = "https://mantenimiento-470311.ew.r.appspot.com"

    # Test directo del endpoint de email
    test_url = f"{base_url}/api/test-email"

    try:
        print("📧 Probando endpoint de test de email...")
        response = requests.get(test_url)

        print(f"📊 Código de respuesta: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Respuesta JSON:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except:
                print(f"📋 Respuesta texto: {response.text}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📋 Respuesta: {response.text[:300]}...")

    except Exception as e:
        print(f"💥 Error en la verificación: {str(e)}")


def verificar_estado_sistema():
    """
    Verificar el estado general del sistema
    """
    print("\n🔧 VERIFICACIÓN DE ESTADO DEL SISTEMA")
    print("=" * 40)

    base_url = "https://mantenimiento-470311.ew.r.appspot.com"

    endpoints = ["/api/health", "/api/diagnostico", "/diagnostico"]

    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"📡 Probando: {endpoint}")
            response = requests.get(url)
            print(f"   📊 Código: {response.status_code}")

            if response.status_code == 200:
                if "json" in response.headers.get("content-type", ""):
                    try:
                        data = response.json()
                        if "email" in str(data).lower() or "mail" in str(data).lower():
                            print(f"   📧 Email info: {data}")
                    except:
                        pass

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


if __name__ == "__main__":
    verificar_email_directo()
    verificar_estado_sistema()
