#!/usr/bin/env python3
"""
Test simple para verificar que la generación automática de códigos
está funcionando correctamente en la interfaz web
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"


def test_categorias_api():
    """Prueba la API de categorías"""
    print("🧪 Probando API de categorías...")

    try:
        response = requests.get(f"{BASE_URL}/api/categorias/")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status 200 - {len(data['categorias'])} categorías encontradas")

            # Mostrar primera categoría para verificar estructura
            if data["categorias"]:
                primera = data["categorias"][0]
                print(
                    f"📋 Primera categoría: {primera['nombre']} (ID: {primera['id']}, Prefijo: {primera['prefijo']})"
                )
                return primera["id"]

        else:
            print(f"❌ Error: Status {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Error de conexión: {e}")

    return None


def test_codigo_generation(categoria_id):
    """Prueba la generación de código para una categoría"""
    if not categoria_id:
        print("⚠️ No hay categoria ID para probar")
        return

    print(f"🧪 Probando generación de código para categoría ID: {categoria_id}...")

    try:
        response = requests.get(f"{BASE_URL}/api/categorias/{categoria_id}/codigo")

        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                print(f"✅ Código generado: {data['codigo']}")
                print(f"📊 Siguiente número: {data['siguiente_numero']}")
            else:
                print(f"❌ Error en generación: {data['message']}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Error de conexión: {e}")


def test_page_accessibility():
    """Verifica que las páginas principales son accesibles"""
    pages = [
        ("/inventario", "Página de inventario"),
        ("/test-codigo-automatico", "Página de test de código automático"),
    ]

    for url, descripcion in pages:
        print(f"🧪 Probando {descripcion}...")
        try:
            response = requests.get(f"{BASE_URL}{url}")
            if response.status_code == 200:
                print(f"✅ {descripcion} accesible")
            else:
                print(f"❌ {descripcion} error {response.status_code}")
        except Exception as e:
            print(f"❌ Error accediendo a {descripcion}: {e}")


if __name__ == "__main__":
    print("🚀 INICIANDO TESTS DE INTEGRACIÓN DE CÓDIGO AUTOMÁTICO")
    print("=" * 60)

    # Test 1: Verificar accesibilidad de páginas
    test_page_accessibility()
    print()

    # Test 2: API de categorías
    categoria_id = test_categorias_api()
    print()

    # Test 3: Generación de códigos
    if categoria_id:
        test_codigo_generation(categoria_id)
        print()

        # Generar varios códigos para verificar incremento
        print("🧪 Generando múltiples códigos para verificar incremento...")
        for i in range(3):
            print(f"🔄 Generación {i+1}/3...")
            test_codigo_generation(categoria_id)
            time.sleep(0.5)

    print("=" * 60)
    print("✅ TESTS COMPLETADOS")
    print()
    print("💡 INSTRUCCIONES PARA VERIFICAR EN BROWSER:")
    print("1. Abrir: http://127.0.0.1:5000/inventario")
    print("2. Hacer clic en 'Nuevo Artículo'")
    print("3. Seleccionar una categoría del dropdown")
    print("4. Verificar que el código se genera automáticamente")
    print("5. Para debug: http://127.0.0.1:5000/test-codigo-automatico")
