import requests
import sys


def test_gmao_user_login():
    """Probar el login después de crear el usuario gmao-user"""

    base_url = "https://mantenimiento-470311.ew.r.appspot.com"

    print("🔍 Probando login después de crear usuario gmao-user...")
    print(f"URL: {base_url}")

    # Crear una sesión para mantener cookies
    session = requests.Session()
    session.headers.update(
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
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

        # 3. Intentar login con CSRF token
        print("\n3. Intentando login con admin/admin123...")

        login_data = {"username": "admin", "password": "admin123"}

        if csrf_token:
            login_data["csrf_token"] = csrf_token

        # Usar el endpoint correcto /login (no /auth/login)
        login_response = session.post(
            f"{base_url}/login", data=login_data, timeout=30, allow_redirects=False
        )
        print(f"   Status: {login_response.status_code}")

        if login_response.status_code == 200:
            print("   ✅ LOGIN EXITOSO! (status 200)")
            return True
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
                return True
            elif "login" in redirect_url:
                print("   ❌ Login falló - redirección de vuelta al login")
                return False
        elif login_response.status_code == 401:
            print("   ❌ Credenciales inválidas o problema de base de datos (401)")
            return False
        elif login_response.status_code == 400:
            print("   ❌ Error CSRF o datos del formulario (400)")
            print(f"   Respuesta: {login_response.text[:200]}...")
            return False
        else:
            print(f"   ❌ Error inesperado: {login_response.status_code}")
            print(f"   Respuesta: {login_response.text[:200]}...")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBA DE LOGIN POST-CREACIÓN USUARIO GMAO-USER")
    print("=" * 60)

    success = test_gmao_user_login()

    print("\n" + "=" * 60)
    if success:
        print("✅ ÉXITO: El login está funcionando!")
        print("🔗 Puedes acceder en: https://mantenimiento-470311.ew.r.appspot.com")
        print("👤 Usuario: admin")
        print("🔑 Contraseña: admin123")
    else:
        print("❌ El login aún no funciona correctamente")
        print("💡 Puede necesitar permisos adicionales para gmao-user")
    print("=" * 60)
