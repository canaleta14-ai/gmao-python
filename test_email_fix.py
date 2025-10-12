import requests
import re
from datetime import datetime


def test_email_final():
    """
    Prueba final de envío de emails con la nueva configuración de Gmail
    """
    print("🧪 PRUEBA FINAL DE EMAILS")
    print("=" * 40)

    base_url = "https://mantenimiento-470311.ew.r.appspot.com"
    email_destino = "j_hidalgo@disfood.com"
    nueva_password = "mqffpsznrqehwzdm"

    print(f"🌐 URL: {base_url}")
    print(f"📧 Email destino: {email_destino}")
    print(f"🔐 Nueva contraseña: {nueva_password}")
    print()

    session = requests.Session()

    try:
        # 1. Obtener página de solicitudes
        print("📋 Obteniendo página de solicitudes...")
        url = f"{base_url}/solicitudes/"
        response = session.get(url)

        if response.status_code != 200:
            print(f"❌ Error obteniendo página: {response.status_code}")
            return

        # 2. Extraer token CSRF
        content = response.text
        csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', content)
        if not csrf_match:
            print("❌ Token CSRF no encontrado")
            return

        csrf_token = csrf_match.group(1)
        print(f"🔐 Token CSRF: {csrf_token[:15]}...")

        # 3. Preparar datos de solicitud
        form_data = {
            "csrf_token": csrf_token,
            "nombre": "Test Email Final",
            "email": email_destino,
            "telefono": "666777888",
            "tipo_servicio": "correctivo",
            "prioridad": "media",
            "descripcion_problema": f'🧪 PRUEBA EMAIL FINAL - {datetime.now().strftime("%H:%M:%S")} - Verificación de notificaciones con nueva contraseña Gmail',
        }

        # 4. Headers necesarios para CSRF
        headers = {
            "Referer": url,
            "Origin": base_url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

        # 5. Enviar solicitud
        print(f"📤 Enviando solicitud...")
        response_final = session.post(url, data=form_data, headers=headers)
        print(f"📝 Respuesta final: {response_final.status_code}")
        print(f"📍 URL final: {response_final.url}")

        if response_final.status_code == 200:
            print("✅ ¡Solicitud creada exitosamente!")
            print("📧 Se deberían haber enviado emails a:")
            print(f"   - Usuario: {email_destino}")
            print(f"   - Admin: {email_destino}")
            print()
            print("🔍 Revisa los logs de la aplicación para confirmar el envío")
        else:
            print(f"❌ Error: {response_final.status_code}")
            print(f"📋 Contenido: {response_final.text[:500]}...")

    except Exception as e:
        print(f"💥 Error en la prueba: {str(e)}")


if __name__ == "__main__":
    test_email_final()
