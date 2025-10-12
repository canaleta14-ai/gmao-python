#!/usr/bin/env python3
"""
Probar API de artículos
"""

from app.factory import create_app

app = create_app()

with app.test_client() as client:
    response = client.get("/lotes/api/articulos")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.get_json()
        print(f'Success: {data.get("success")}')
        print(f'Articulos: {len(data.get("articulos", []))}')
        for art in data.get("articulos", []):
            print(f'  - {art["codigo"]}: {art["nombre"]}')
    else:
        print(f"Error: {response.data}")
