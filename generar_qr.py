#!/usr/bin/env python3
"""
Generador de código QR para acceso móvil a GMAO Sistema
"""
import qrcode
from PIL import Image

# URL de la aplicación
url = "https://gmao-sistema-2025.ew.r.appspot.com"

# Crear el código QR
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

qr.add_data(url)
qr.make(fit=True)

# Crear imagen
img = qr.make_image(fill_color="black", back_color="white")

# Guardar imagen
img.save("qr_gmao_acceso.png")

print("=" * 60)
print("✅ CÓDIGO QR GENERADO EXITOSAMENTE")
print("=" * 60)
print(f"\n📱 URL: {url}")
print(f"\n💾 Archivo guardado: qr_gmao_acceso.png")
print("\n🔐 Credenciales de acceso:")
print("   Usuario: admin")
print("   Contraseña: admin123")
print("\n📋 Instrucciones:")
print("   1. Abre el archivo 'qr_gmao_acceso.png'")
print("   2. Escanea el código QR con la cámara de tu móvil")
print("   3. Se abrirá automáticamente la aplicación")
print("   4. Inicia sesión con las credenciales anteriores")
print("\n" + "=" * 60)

# También mostrar el QR en consola (ASCII)
print("\n🖼️  CÓDIGO QR (versión texto para consola):\n")
qr.print_ascii(invert=True)
print("\n" + "=" * 60)
