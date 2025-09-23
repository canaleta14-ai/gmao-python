#!/usr/bin/env python
# Test simple de endpoints
import sys

sys.path.insert(0, r"c:\gmao - copia\.venv\Lib\site-packages")

import requests

try:
    print("🔍 Probando endpoint de estadísticas...")
    response = requests.get("http://127.0.0.1:5000/inventario/api/estadisticas")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Estadísticas obtenidas: {data}")
    else:
        print(f"❌ Error: {response.text}")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50 + "\n")

try:
    print("📦 Probando endpoint de artículos...")
    response = requests.get("http://127.0.0.1:5000/inventario/api/articulos")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Total: {data.get('total', 0)}")
        print(f"✅ Artículos: {len(data.get('articulos', []))}")
    else:
        print(f"❌ Error: {response.text}")

except Exception as e:
    print(f"❌ Error: {e}")
