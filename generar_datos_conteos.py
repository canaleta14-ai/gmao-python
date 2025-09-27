#!/usr/bin/env python3
"""
Script para generar datos de prueba para el módulo de conteos
"""

import requests
import json


def generar_datos_conteos():
    """Genera datos de prueba para conteos"""

    print("🚀 Generando datos de prueba para conteos...")

    try:
        # 1. Generar conteos aleatorios
        print("\n1️⃣ Generando conteos aleatorios...")
        response = requests.post(
            "http://127.0.0.1:5000/inventario/api/conteos/aleatorios",
            json={"cantidad": 8},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"  ✅ {data.get('message', 'Conteos generados')}")
            else:
                print(f"  ⚠️  Error: {data.get('error')}")
        else:
            print(f"  ❌ Error HTTP: {response.status_code}")
            print(f"  Respuesta: {response.text}")

        # 2. Crear un período de inventario
        print("\n2️⃣ Creando período de inventario...")
        periodo_data = {
            "año": 2025,
            "mes": 9,
            "usuario_responsable": "Sistema Test",
            "observaciones": "Período de prueba generado automáticamente",
        }

        response = requests.post(
            "http://127.0.0.1:5000/inventario/api/periodos-inventario",
            json=periodo_data,
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"  ✅ {data.get('message', 'Período creado')}")
            else:
                print(f"  ⚠️  Error: {data.get('error')}")
        else:
            print(f"  ❌ Error HTTP: {response.status_code}")
            print(f"  Respuesta: {response.text}")

        # 3. Verificar el resumen actualizado
        print("\n3️⃣ Verificando resumen actualizado...")
        response = requests.get(
            "http://127.0.0.1:5000/inventario/api/conteos/resumen", timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                resumen = data["resumen"]
                print(f"  ✅ Período actual: {resumen.get('periodo_actual')}")
                print(f"  ✅ Total conteos: {resumen.get('total_conteos')}")
                print(f"  ✅ Pendientes: {resumen.get('conteos_pendientes')}")
                print(f"  ✅ Con diferencias: {resumen.get('conteos_diferencias')}")
            else:
                print(f"  ⚠️  Error: {data.get('error')}")
        else:
            print(f"  ❌ Error HTTP: {response.status_code}")

        # 4. Listar algunos conteos generados
        print("\n4️⃣ Listando conteos generados...")
        response = requests.get(
            "http://127.0.0.1:5000/inventario/api/conteos?per_page=5", timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("conteos"):
                print(f"  ✅ {len(data['conteos'])} conteos encontrados:")
                for i, conteo in enumerate(data["conteos"][:3], 1):
                    articulo = conteo.get("articulo", {})
                    print(
                        f"    {i}. {articulo.get('codigo')} - {conteo.get('tipo_conteo')} - {conteo.get('estado')}"
                    )
            else:
                print(f"  ⚠️  No hay conteos o error: {data.get('error')}")
        else:
            print(f"  ❌ Error HTTP: {response.status_code}")

        print(f"\n🎯 Datos de prueba generados exitosamente!")
        print(f"   Ahora puedes:")
        print(f"   1. Ir a http://127.0.0.1:5000/inventario/conteos")
        print(f"   2. Ver los conteos generados")
        print(f"   3. Procesar conteos pendientes")
        print(f"   4. Filtrar por tipo y estado")
        print(f"   5. Generar más conteos aleatorios")

    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor Flask")
        print(
            "   Asegúrate de que la aplicación esté ejecutándose en http://127.0.0.1:5000"
        )
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 GENERADOR DE DATOS DE PRUEBA - MÓDULO CONTEOS")
    print("=" * 60)
    generar_datos_conteos()
    print("=" * 60)
