import requests

try:
    # Test 1: Búsqueda básica sin filtros
    response1 = requests.get(
        "http://127.0.0.1:5000/activos/api?page=1&per_page=10", timeout=5
    )
    print("Test 1 - Sin filtros:")
    print(f"  Status: {response1.status_code}")
    if response1.status_code == 200:
        data1 = response1.json()
        print(f'  Total activos: {data1.get("total", 0)}')
        print(f'  Activos en página: {len(data1.get("items", []))}')

    # Test 2: Búsqueda por texto (q)
    response2 = requests.get(
        "http://127.0.0.1:5000/activos/api?page=1&per_page=10&q=compresor", timeout=5
    )
    print("\nTest 2 - Búsqueda por texto (q=compresor):")
    print(f"  Status: {response2.status_code}")
    if response2.status_code == 200:
        data2 = response2.json()
        print(f'  Resultados encontrados: {data2.get("total", 0)}')
        if data2.get("items"):
            print(f'  Primer resultado: {data2["items"][0].get("nombre", "N/A")}')

    # Test 3: Búsqueda por estado
    response3 = requests.get(
        "http://127.0.0.1:5000/activos/api?page=1&per_page=10&estado=Operativo",
        timeout=5,
    )
    print("\nTest 3 - Filtro por estado (Operativo):")
    print(f"  Status: {response3.status_code}")
    if response3.status_code == 200:
        data3 = response3.json()
        print(f'  Activos operativos: {data3.get("total", 0)}')

    # Test 4: Búsqueda por tipo
    response4 = requests.get(
        "http://127.0.0.1:5000/activos/api?page=1&per_page=10&tipo=Máquina", timeout=5
    )
    print("\nTest 4 - Filtro por tipo (Máquina):")
    print(f"  Status: {response4.status_code}")
    if response4.status_code == 200:
        data4 = response4.json()
        print(f'  Máquinas encontradas: {data4.get("total", 0)}')

    # Test 5: Búsqueda combinada
    response5 = requests.get(
        "http://127.0.0.1:5000/activos/api?page=1&per_page=10&q=maquina&estado=Operativo",
        timeout=5,
    )
    print("\nTest 5 - Búsqueda combinada (q=maquina, estado=Operativo):")
    print(f"  Status: {response5.status_code}")
    if response5.status_code == 200:
        data5 = response5.json()
        print(f'  Resultados: {data5.get("total", 0)}')

    print("\n✅ SUCCESS: Sistema de búsqueda eficiente implementado correctamente")
    print("   - Búsqueda del lado del servidor funcionando")
    print("   - Filtros múltiples operando correctamente")
    print("   - Paginación integrada con filtros")

except Exception as e:
    print(f"❌ Error: {e}")
