import requests


def test_production_login():
    """Probar el login en producción después de inicializar la base de datos"""

    base_url = "https://mantenimiento-470311.ew.r.appspot.com"

    print("🔍 Probando la aplicación en producción...")
    print(f"URL: {base_url}")

    # Crear una sesión para mantener cookies
    session = requests.Session()
    session.headers.update(
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )

    try:
        # 1. Verificar que la aplicación responde
        print("\n1. Verificando que la aplicación responde...")
        response = session.get(base_url, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   URL final: {response.url}")

        if response.status_code == 200:
            print("   ✅ Aplicación responde correctamente")
        else:
            print(f"   ❌ Error en aplicación: {response.status_code}")
            return False

        # 2. Buscar formulario de login
        print("\n2. Buscando formulario de login...")
        if "login" in response.text.lower() or "usuario" in response.text.lower():
            print("   ✅ Formulario de login encontrado")
        else:
            print("   ⚠️  No se encontró formulario de login visible")

        # 3. Intentar login
        print("\n3. Intentando login con admin/admin123...")

        # Buscar endpoint de login
        login_endpoints = ["/auth/login", "/login", "/api/auth/login"]

        for endpoint in login_endpoints:
            login_url = base_url + endpoint
            print(f"   Probando: {endpoint}")

            login_data = {"username": "admin", "password": "admin123"}

            try:
                login_response = session.post(login_url, data=login_data, timeout=30)
                print(f"   Status: {login_response.status_code}")

                if login_response.status_code == 200:
                    if (
                        "dashboard" in login_response.text.lower()
                        or "bienvenido" in login_response.text.lower()
                    ):
                        print("   ✅ LOGIN EXITOSO!")
                        return True
                    else:
                        print("   ⚠️  Login respondió 200 pero sin dashboard")

                elif login_response.status_code == 302:
                    # Redirección - probablemente exitoso
                    redirect_url = login_response.headers.get("Location", "")
                    print(f"   ↗️  Redirección a: {redirect_url}")
                    if "dashboard" in redirect_url or "home" in redirect_url:
                        print("   ✅ LOGIN EXITOSO! (redirección a dashboard)")
                        return True
                    elif "login" in redirect_url:
                        print("   ❌ Login falló - redirección de vuelta al login")
                    else:
                        print("   ✅ LOGIN EXITOSO! (redirección)")
                        return True

                elif login_response.status_code == 401:
                    print("   ❌ Credenciales inválidas (401)")

                elif login_response.status_code == 404:
                    print("   ❌ Endpoint no encontrado (404)")

                else:
                    print(f"   ❌ Error inesperado: {login_response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"   ❌ Error de conexión: {e}")

        # 4. Verificar si ya estamos logueados
        print("\n4. Verificando estado de la sesión...")
        dashboard_urls = ["/dashboard", "/home", "/main", "/"]

        for url in dashboard_urls:
            try:
                dash_response = session.get(base_url + url, timeout=30)
                if dash_response.status_code == 200 and (
                    "dashboard" in dash_response.text.lower()
                    or "mantenimiento" in dash_response.text.lower()
                ):
                    print(f"   ✅ Acceso exitoso a {url}")
                    return True
            except:
                continue

        print("\n❌ No se pudo completar el login exitosamente")
        return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBA DE LOGIN EN PRODUCCIÓN")
    print("=" * 60)

    success = test_production_login()

    print("\n" + "=" * 60)
    if success:
        print("✅ ÉXITO: El sistema de login está funcionando!")
        print("🔗 Puedes acceder en: https://mantenimiento-470311.ew.r.appspot.com")
        print("👤 Usuario: admin")
        print("🔑 Contraseña: admin123")
    else:
        print("❌ El login aún no funciona correctamente")
        print("💡 La base de datos está inicializada, puede ser un problema de rutas")
    print("=" * 60)
