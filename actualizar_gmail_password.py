#!/usr/bin/env python3
"""
Script para actualizar la contraseña de email en Secret Manager
"""

import subprocess
import sys


def actualizar_password_gmail():
    """Actualizar la contraseña de Gmail en Secret Manager"""

    print("🔧 ACTUALIZACIÓN DE CONTRASEÑA GMAIL")
    print("=" * 50)
    print()
    print("❌ PROBLEMA ACTUAL:")
    print("   Gmail rechaza la contraseña: dvematimfpjjpxji")
    print("   Error: 'Username and Password not accepted'")
    print()
    print("✅ SOLUCIÓN:")
    print("   1. Ir a: https://myaccount.google.com/apppasswords")
    print("   2. Crear nueva 'App Password' para GMAO")
    print("   3. Actualizar secret en Google Cloud")
    print()

    nueva_password = input(
        "📝 Ingresa la nueva contraseña de aplicación de Gmail: "
    ).strip()

    if not nueva_password:
        print("❌ No se ingresó contraseña. Cancelando...")
        return

    if len(nueva_password) < 10:
        print("⚠️  La contraseña parece muy corta. ¿Estás seguro? (s/n): ", end="")
        confirmar = input().lower()
        if confirmar != "s":
            print("❌ Cancelando...")
            return

    try:
        print("🔄 Actualizando secret gmao-mail-password...")

        # Comando para actualizar el secret
        cmd = [
            "gcloud",
            "secrets",
            "versions",
            "add",
            "gmao-mail-password",
            "--data-file=-",
        ]

        # Ejecutar comando con la nueva contraseña
        result = subprocess.run(
            cmd, input=nueva_password.encode(), capture_output=True, text=False
        )

        if result.returncode == 0:
            print("✅ Secret actualizado exitosamente")
            print()
            print("🚀 PRÓXIMOS PASOS:")
            print("1. La nueva contraseña está configurada en Secret Manager")
            print(
                "2. La aplicación la obtendrá automáticamente en la próxima solicitud"
            )
            print("3. Probar creando una nueva solicitud")
            print()
            print("📧 VERIFICAR:")
            print(
                "   - Crear solicitud en: https://mantenimiento-470311.ew.r.appspot.com/solicitudes"
            )
            print("   - Verificar email en: j_hidalgo@gmail.com")
            print("   - Revisar logs: gcloud app logs tail -s default")

        else:
            print(f"❌ Error actualizando secret: {result.stderr.decode()}")

    except Exception as e:
        print(f"❌ Error: {e}")


def mostrar_instrucciones_gmail():
    """Mostrar instrucciones detalladas para Gmail"""
    print("\n📧 INSTRUCCIONES GMAIL APP PASSWORD:")
    print("=" * 50)
    print("1. Ir a: https://myaccount.google.com/apppasswords")
    print("2. Si aparece 'App passwords isn't available', verificar:")
    print("   - Tener verificación en 2 pasos activada")
    print("   - Usar cuenta personal (no organizacional)")
    print("3. Crear nueva App Password:")
    print("   - Seleccionar app: 'Mail'")
    print("   - Seleccionar dispositivo: 'Other (custom name)'")
    print("   - Nombre: 'GMAO Sistema'")
    print("4. Copiar la contraseña de 16 caracteres (ej: abcd efgh ijkl mnop)")
    print("5. Usar esa contraseña aquí (sin espacios)")


if __name__ == "__main__":
    mostrar_instrucciones_gmail()
    print()
    actualizar_password_gmail()
