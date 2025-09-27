#!/usr/bin/env python3
"""
Test para verificar el filtrado de la API de artículos
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.controllers.inventario_controller_simple import listar_articulos_avanzado


def test_api_filtering():
    """Test para verificar que el filtro busqueda_general funcione"""
    app = create_app()

    with app.app_context():
        print("🧪 Probando filtros de API...")

        # Test 1: Sin filtros (todos los artículos)
        print("\n1️⃣ Sin filtros:")
        articulos, total = listar_articulos_avanzado({}, 1, 5)
        print(f"   Total sin filtros: {total}")
        if articulos:
            for i, art in enumerate(articulos[:3]):
                print(f"   {i+1}. {art.codigo} - {art.descripcion[:50]}...")

        # Test 2: Con filtro de búsqueda general 'her'
        print("\n2️⃣ Con filtro 'her':")
        filtros = {"busqueda_general": "her"}
        articulos, total = listar_articulos_avanzado(filtros, 1, 5)
        print(f"   Total con filtro 'her': {total}")
        if articulos:
            for i, art in enumerate(articulos):
                print(f"   {i+1}. {art.codigo} - {art.descripcion[:50]}...")
        else:
            print("   ❌ Sin resultados con 'her'")

        # Test 3: Con filtro de búsqueda general 'm'
        print("\n3️⃣ Con filtro 'm':")
        filtros = {"busqueda_general": "m"}
        articulos, total = listar_articulos_avanzado(filtros, 1, 5)
        print(f"   Total con filtro 'm': {total}")
        if articulos:
            for i, art in enumerate(articulos):
                print(f"   {i+1}. {art.codigo} - {art.descripcion[:50]}...")
        else:
            print("   ❌ Sin resultados con 'm'")

        # Test 4: Con filtro que no debería dar resultados
        print("\n4️⃣ Con filtro 'xyz123':")
        filtros = {"busqueda_general": "xyz123"}
        articulos, total = listar_articulos_avanzado(filtros, 1, 5)
        print(f"   Total con filtro 'xyz123': {total}")
        if articulos:
            print("   ⚠️ Encontró artículos inesperadamente")
        else:
            print("   ✅ Sin resultados como esperado")


if __name__ == "__main__":
    test_api_filtering()
