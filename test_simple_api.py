#!/usr/bin/env python
# Test simple de endpoints
import sys

sys.path.insert(0, r"c:\gmao - copia\.venv\Lib\site-packages")

import requests

try:
    print("ğŸ”� Probando endpoint de estadÃ­sticas...")
    response = requests.get("http://127.0.0.1:5000/inventario/api/estadisticas")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"âœ… EstadÃ­sticas obtenidas: {data}")
    else:
        print(f"â�Œ Error: {response.text}")

except Exception as e:
    print(f"â�Œ Error: {e}")

print("\n" + "=" * 50 + "\n")

try:
    print("ğŸ“¦ Probando endpoint de artÃ­culos...")
    response = requests.get("http://127.0.0.1:5000/inventario/api/articulos")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"âœ… Total: {data.get('total', 0)}")
        print(f"âœ… ArtÃ­culos: {len(data.get('articulos', []))}")
    else:
        print(f"â�Œ Error: {response.text}")

except Exception as e:
    print(f"â�Œ Error: {e}")
