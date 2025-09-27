#!/usr/bin/env python3
"""
Script simple para probar el módulo de conteos
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000/inventario"


def test_conteos():
    print("🧪 PRUEBA SIMPLE DEL MÓDULO CONTEOS")
    print("=" * 50)

    # 1. Obtener resumen inicial
    print("1️⃣ Obteniendo resumen inicial...")
    try:
        response = requests.get(f"{BASE_URL}/api/conteos/resumen")
        if response.status_code == 200:
            data = response.json()
            resumen = data["resumen"]
            print(f"  ✅ Total conteos: {resumen['total_conteos']}")
            print(f"  ✅ Pendientes: {resumen['conteos_pendientes']}")
        else:
            print(f"  ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # 2. Generar más conteos si es necesario
    if resumen.get("total_conteos", 0) < 5:
        print("\n2️⃣ Generando conteos adicionales...")
        try:
            response = requests.post(
                f"{BASE_URL}/api/conteos/aleatorios", json={"cantidad": 5}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ {data.get('message', 'Conteos generados')}")
            else:
                print(f"  ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    # 3. Listar algunos conteos
    print("\n3️⃣ Listando conteos...")
    try:
        response = requests.get(f"{BASE_URL}/api/conteos?per_page=3")
        if response.status_code == 200:
            data = response.json()
            conteos = data.get("conteos", [])
            print(f"  ✅ Se encontraron {len(conteos)} conteos:")
            for conteo in conteos[:3]:
                articulo = conteo.get("articulo", {})
                print(
                    f"    • {articulo.get('codigo', 'N/A')} - {conteo.get('estado', 'N/A')}"
                )
        else:
            print(f"  ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # 4. Crear período
    print("\n4️⃣ Creando período de inventario...")
    try:
        periodo_data = {
            "año": 2025,
            "mes": 9,
            "usuario_responsable": "Test Admin",
            "observaciones": "Periodo de prueba automatizado",
        }
        response = requests.post(
            f"{BASE_URL}/api/periodos-inventario", json=periodo_data
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ {data.get('message', 'Periodo creado')}")
        else:
            print(f"  ❌ Error: {response.status_code}")
            print(f"  Respuesta: {response.text}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print("\n🎯 PRUEBA COMPLETADA!")
    print("\n📋 ACCIONES DISPONIBLES:")
    print("   • Ve a http://127.0.0.1:5000/inventario/conteos")
    print("   • Genera conteos aleatorios")
    print("   • Procesa conteos pendientes")
    print("   • Filtra por tipo y estado")


if __name__ == "__main__":
    test_conteos()
