import requests
import sys


def test_login_with_proper_headers():
    """Probar el login con headers correctos para evitar errores CSRF"""

    base_url = "https://mantenimiento-470311.ew.r.appspot.com"

    print("🔍 Probando login con headers correctos...")
    print(f"URL: {base_url}")

    # Crear una sesión para mantener cookies
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    )

    try:
        # 1. Ir a la página de login para obtener CSRF token
        print("\n1. Obteniendo página de login...")
        login_page = session.get(f"{base_url}/login", timeout=30)
        print(f"   Status: {login_page.status_code}")

        if login_page.status_code != 200:
            print(f"   ❌ Error obteniendo página de login: {login_page.status_code}")
            return False

        # 2. Extraer CSRF token del HTML
        print("\n2. Extrayendo CSRF token...")
        csrf_token = None
        if "csrf_token" in login_page.text:
            import re

            csrf_match = re.search(
                r'name="csrf_token"[^>]*value="([^"]*)"', login_page.text
            )
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"   ✅ CSRF token encontrado: {csrf_token[:20]}...")
            else:
                print("   ⚠️  CSRF token no encontrado en el HTML")

        # 3. Intentar login con headers correctos
        print("\n3. Intentando login con admin/admin123...")

        login_data = {"username": "admin", "password": "admin123"}

        if csrf_token:
            login_data["csrf_token"] = csrf_token

        # Headers específicos para el POST
        login_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": f"{base_url}/login",
            "Origin": base_url,
        }

        # Actualizar headers para este request
        session.headers.update(login_headers)

        # Usar el endpoint correcto /login
        login_response = session.post(
            f"{base_url}/login", data=login_data, timeout=30, allow_redirects=False
        )
        print(f"   Status: {login_response.status_code}")

        if login_response.status_code == 200:
            if (
                "dashboard" in login_response.text.lower()
                or "bienvenido" in login_response.text.lower()
            ):
                print("   ✅ LOGIN EXITOSO! (dashboard en respuesta)")
                return True
            elif (
                "error" in login_response.text.lower()
                or "incorrecto" in login_response.text.lower()
            ):
                print("   ❌ Credenciales incorrectas")
                return False
            else:
                print("   ⚠️  Respuesta 200 pero contenido unclear")
                return False
        elif login_response.status_code == 302:
            # Redirección - probablemente exitoso
            redirect_url = login_response.headers.get("Location", "")
            print(f"   ↗️  Redirección a: {redirect_url}")
            if (
                "dashboard" in redirect_url
                or "home" in redirect_url
                or redirect_url == "/"
            ):
                print("   ✅ LOGIN EXITOSO! (redirección exitosa)")

                # Seguir la redirección para confirmar
                follow_response = session.get(f"{base_url}{redirect_url}", timeout=30)
                print(f"   Following redirect status: {follow_response.status_code}")
                return True
            elif "login" in redirect_url:
                print("   ❌ Login falló - redirección de vuelta al login")
                return False
        elif login_response.status_code == 401:
            print("   ❌ Credenciales inválidas (401)")
            return False
        elif login_response.status_code == 400:
            print("   ❌ Error CSRF o datos del formulario (400)")
            print(f"   Respuesta: {login_response.text[:300]}...")
            return False
        else:
            print(f"   ❌ Error inesperado: {login_response.status_code}")
            print(f"   Respuesta: {login_response.text[:300]}...")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBA DE LOGIN CON HEADERS CORRECTOS")
    print("=" * 60)

    success = test_login_with_proper_headers()

    print("\n" + "=" * 60)
    if success:
        print("✅ ÉXITO: El login está funcionando!")
        print("🔗 Puedes acceder en: https://mantenimiento-470311.ew.r.appspot.com")
        print("👤 Usuario: admin")
        print("🔑 Contraseña: admin123")
    else:
        print("❌ El login aún no funciona correctamente")
        print("💡 Revisando configuración CSRF...")
    print("=" * 60)
