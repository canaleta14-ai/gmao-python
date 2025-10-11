#!/usr/bin/env python3
"""
Script para probar la subida de archivos al sistema GMAO
"""

import requests
import tempfile
import os


def test_file_upload():
    """Probar subida de archivos"""

    print("🧪 PRUEBA DE SUBIDA DE ARCHIVOS")
    print("=" * 50)

    base_url = "http://localhost:5000"

    # 1. Login primero
    print("🔐 Haciendo login...")
    session = requests.Session()

    # Obtener página de login para token CSRF
    response = session.get(f"{base_url}/login")
    if response.status_code != 200:
        print("❌ Error obteniendo página de login")
        return False

    # Extraer token CSRF
    import re

    csrf_pattern = r'name="csrf_token" value="([^"]+)"'
    csrf_match = re.search(csrf_pattern, response.text)

    if not csrf_match:
        print("❌ Token CSRF no encontrado")
        return False

    csrf_token = csrf_match.group(1)

    # Login
    login_data = {"username": "admin", "password": "admin123", "csrf_token": csrf_token}

    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code != 302:
        print(f"❌ Error en login: {response.status_code}")
        return False

    print("✅ Login exitoso")

    # 2. Verificar que existe al menos un activo
    print("🔍 Verificando activos...")
    response = session.get(f"{base_url}/activos/api?page=1&per_page=1")
    if response.status_code != 200:
        print("❌ Error obteniendo activos")
        return False

    data = response.json()
    if data.get("total", 0) == 0:
        print("⚠️ No hay activos para probar manuales")
        return False

    activo_id = data["items"][0]["id"]
    print(f"✅ Usando activo ID: {activo_id}")

    # 3. Crear archivo temporal de prueba
    print("📝 Creando archivo de prueba...")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Este es un manual de prueba para el sistema GMAO.\n")
        f.write("Contenido de ejemplo para verificar la subida de archivos.\n")
        f.write(f"Generado el: {os.popen('date /t').read().strip()}\n")
        temp_file = f.name

    print(f"✅ Archivo creado: {temp_file}")

    # 4. Probar subida de manual
    print("📤 Probando subida de manual...")

    # Obtener token CSRF para el formulario de manual
    response = session.get(f"{base_url}/activos/api/{activo_id}/manuales")
    if response.status_code != 200:
        print(f"❌ Error obteniendo página de manuales: {response.status_code}")
        return False

    # Subir archivo
    with open(temp_file, "rb") as f:
        files = {"archivo": ("manual_prueba.txt", f, "text/plain")}
        data = {
            "tipo": "Manual de Prueba",
            "descripcion": "Archivo de prueba para validar el sistema de almacenamiento local",
        }

        response = session.post(
            f"{base_url}/activos/api/{activo_id}/manuales", files=files, data=data
        )

        print(f"📊 Respuesta de subida: {response.status_code}")

        if response.status_code == 200:
            print("✅ ¡Archivo subido exitosamente!")

            # Verificar que el archivo se guardó
            upload_dir = os.path.join(os.path.dirname(__file__), "uploads", "manuales")
            if os.path.exists(upload_dir):
                files_in_dir = os.listdir(upload_dir)
                print(f"📁 Archivos en uploads/manuales: {files_in_dir}")
                if files_in_dir:
                    print("✅ Archivo guardado localmente")
                else:
                    print("⚠️ Directorio vacío")

            return True
        else:
            print(f"❌ Error en subida: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Respuesta: {response.text[:200]}...")
            return False

    # Limpiar archivo temporal
    try:
        os.unlink(temp_file)
        print("🗑️ Archivo temporal eliminado")
    except:
        pass


if __name__ == "__main__":
    try:
        success = test_file_upload()
        if success:
            print("\n🎉 ¡PRUEBA DE ARCHIVOS EXITOSA!")
            print("✅ Sistema de almacenamiento local funcionando")
        else:
            print("\n❌ Prueba de archivos falló")
            print("🔧 Revisar configuración de storage")
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        import traceback

        traceback.print_exc()
