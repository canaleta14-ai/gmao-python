#!/usr/bin/env python3
"""
Script de debug para probar el dashboard manualmente
"""

import requests
import json


def test_dashboard():
    print("🔍 Probando el dashboard...")

    # Probar endpoint de estadísticas
    try:
        response = requests.get("http://127.0.0.1:5000/api/estadisticas")
        print(f"✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("📊 Datos del endpoint:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            # Simular la lógica JavaScript
            completadas = data.get("ordenes_por_estado", {}).get("Completada", 0)
            pendientes = data.get("ordenes_por_estado", {}).get("Pendiente", 0)
            en_proceso = data.get("ordenes_por_estado", {}).get("En Proceso", 0)
            total_activos = data.get("total_activos", 0)

            activas = pendientes + en_proceso

            print("\n🎯 Valores esperados en el dashboard:")
            print(f"  - Órdenes Activas: {activas}")
            print(f"  - Completadas: {completadas}")
            print(f"  - Pendientes: {pendientes}")
            print(f"  - Total Activos: {total_activos}")
        else:
            print(f"❌ Error en el endpoint: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor Flask")
        print("   Asegúrate de que Flask esté ejecutándose en http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    test_dashboard()
