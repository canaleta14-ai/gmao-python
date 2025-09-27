#!/usr/bin/env python3
"""
Script para diagnosticar problemas con el módulo de conteos
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000/inventario"


def test_conteos_debug():
    print("🔍 DIAGNÓSTICO DEL MÓDULO CONTEOS")
    print("=" * 50)

    # 1. Verificar resumen
    print("1️⃣ API Resumen...")
    try:
        response = requests.get(f"{BASE_URL}/api/conteos/resumen", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            resumen = data.get("resumen", {})
            print(f"   ✅ Total conteos: {resumen.get('total_conteos', 0)}")
            print(f"   ✅ Pendientes: {resumen.get('conteos_pendientes', 0)}")
            print(f"   ✅ Período: {resumen.get('periodo_actual', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")

    # 2. Verificar API de listado
    print("\n2️⃣ API Listado...")
    try:
        response = requests.get(f"{BASE_URL}/api/conteos?per_page=3", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            conteos = data.get("conteos", [])
            print(f"   ✅ Conteos recibidos: {len(conteos)}")

            if conteos:
                conteo = conteos[0]
                print(f"   📋 Primer conteo:")
                print(f"      - ID: {conteo.get('id')}")
                print(f"      - Fecha: {conteo.get('fecha_conteo')}")
                print(
                    f"      - Artículo: {conteo.get('articulo', {}).get('codigo', 'N/A')}"
                )
                print(f"      - Estado: {conteo.get('estado')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")

    # 3. Verificar página web
    print("\n3️⃣ Página Web...")
    try:
        response = requests.get(f"{BASE_URL}/conteos", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            content = response.text
            # Buscar elementos clave
            checks = [
                ("tabla-conteos", "tabla-conteos" in content),
                ("conteos.js", "conteos.js" in content),
                ("tabla-conteos-body", "tabla-conteos-body" in content),
                ("total-conteos", "total-conteos" in content),
            ]

            for check, found in checks:
                status = "✅" if found else "❌"
                print(f"   {status} {check}: {'Presente' if found else 'Ausente'}")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")

    # 4. Generar un conteo para tener datos frescos
    print("\n4️⃣ Generar Conteo de Prueba...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/conteos/aleatorios", json={"cantidad": 1}, timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {data.get('message', 'Conteo generado')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")


if __name__ == "__main__":
    test_conteos_debug()
