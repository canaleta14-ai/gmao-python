import requests


def trigger_database_init():
    """Hacer una petición HTTP para activar la inicialización de base de datos"""

    base_url = "https://mantenimiento-470311.ew.r.appspot.com"

    print("🔧 Intentando activar inicialización de base de datos...")

    # URLs que podrían activar la inicialización automática
    init_urls = [
        f"{base_url}/api/cron/aplicar-parches-db",  # URL de parches que vimos en logs
        f"{base_url}/",  # Homepage que podría hacer verificaciones
        f"{base_url}/login",  # Login que debería verificar tablas
    ]

    session = requests.Session()
    session.headers.update(
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )

    for url in init_urls:
        try:
            print(f"   Probando: {url}")
            response = session.get(url, timeout=30)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                print(f"   ✅ Respuesta exitosa")
            elif response.status_code == 500:
                print(f"   ⚠️  Error 500 - posible inicialización de DB")
            else:
                print(f"   ℹ️  Status: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n🔄 Esperando 5 segundos para que se procesen inicializaciones...")
    import time

    time.sleep(5)


def main():
    print("=" * 60)
    print("ACTIVACIÓN DE INICIALIZACIÓN DE BASE DE DATOS")
    print("=" * 60)

    # Activar procesos de inicialización
    trigger_database_init()

    # Ahora probar login
    print("\n🔐 Probando login después de la activación...")

    base_url = "https://mantenimiento-470311.ew.r.appspot.com"
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        }
    )

    try:
        # Obtener página de login
        login_page = session.get(f"{base_url}/login", timeout=30)
        print(f"   Login page status: {login_page.status_code}")

        if login_page.status_code == 200:
            # Extraer CSRF token
            import re

            csrf_match = re.search(
                r'name="csrf_token"[^>]*value="([^"]*)"', login_page.text
            )
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"   ✅ CSRF token obtenido")

                # Intentar login
                login_data = {
                    "username": "admin",
                    "password": "admin123",
                    "csrf_token": csrf_token,
                }

                login_headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Referer": f"{base_url}/login",
                    "Origin": base_url,
                }
                session.headers.update(login_headers)

                login_response = session.post(
                    f"{base_url}/login",
                    data=login_data,
                    timeout=30,
                    allow_redirects=False,
                )
                print(f"   Login status: {login_response.status_code}")

                if login_response.status_code == 302:
                    redirect_url = login_response.headers.get("Location", "")
                    print(f"   ↗️  Redirección: {redirect_url}")
                    if "dashboard" in redirect_url or redirect_url == "/":
                        print("   ✅ ¡LOGIN EXITOSO!")
                        return True
                    elif "login" in redirect_url:
                        print("   ❌ Login falló - redirección a login")
                        return False
                elif login_response.status_code == 401:
                    print("   ❌ Credenciales inválidas (401)")
                    return False
                elif login_response.status_code == 200:
                    if "dashboard" in login_response.text.lower():
                        print("   ✅ ¡LOGIN EXITOSO!")
                        return True
                    else:
                        print("   ❌ Login falló (200 pero sin dashboard)")
                        return False
                else:
                    print(f"   ❌ Status inesperado: {login_response.status_code}")
                    return False
            else:
                print("   ❌ No se pudo extraer CSRF token")
                return False
        else:
            print(f"   ❌ Error obteniendo login page: {login_page.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False


if __name__ == "__main__":
    success = main()

    print("\n" + "=" * 60)
    if success:
        print("✅ ¡ÉXITO! El sistema está funcionando")
        print("🔗 URL: https://mantenimiento-470311.ew.r.appspot.com")
        print("👤 Usuario: admin")
        print("🔑 Contraseña: admin123")
    else:
        print("❌ Aún hay problemas con el login")
        print("💡 La base de datos puede necesitar inicialización manual")
    print("=" * 60)
