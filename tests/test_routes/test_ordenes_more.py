import pytest


def _crear_orden(authenticated_client, tipo="Correctivo", prioridad="Media", descripcion="Orden test"):
    resp = authenticated_client.post(
        "/ordenes/",
        json={"tipo": tipo, "prioridad": prioridad, "descripcion": descripcion},
    )
    assert resp.status_code in [200, 201]
    return (resp.get_json() or {}).get("id")


def test_listar_ordenes_con_filtros(authenticated_client):
    # Crear dos órdenes con tipos/prioridades distintos
    _crear_orden(authenticated_client, tipo="Correctivo", prioridad="Alta", descripcion="Filtro A")
    _crear_orden(authenticated_client, tipo="Preventivo", prioridad="Baja", descripcion="Filtro B")

    # Filtro de tipo
    r1 = authenticated_client.get("/ordenes/api?tipo=Correctivo&limit=5")
    assert r1.status_code == 200
    data1 = r1.get_json()
    assert isinstance(data1, list)

    # Filtro de prioridad
    r2 = authenticated_client.get("/ordenes/api?prioridad=Baja&limit=5")
    assert r2.status_code == 200
    data2 = r2.get_json()
    assert isinstance(data2, list)

    # Búsqueda por q y estado
    r3 = authenticated_client.get("/ordenes/api?q=Filtro&page=1&per_page=2&estado=Pendiente")
    assert r3.status_code == 200
    data3 = r3.get_json()
    # Paginado
    for key in ["items", "page", "per_page", "total"]:
        assert key in data3


def test_obtener_orden_404(authenticated_client):
    resp = authenticated_client.get("/ordenes/api/999999")
    assert resp.status_code == 404
    data = resp.get_json() or {}
    assert "error" in data


def test_actualizar_orden_campos_requeridos(authenticated_client):
    # Crear orden
    orden_id = _crear_orden(authenticated_client, descripcion="Actualizar requeridos")

    # Intentar actualizar con descripción vacía
    r1 = authenticated_client.put(
        f"/ordenes/api/{orden_id}", json={"tipo": "Correctivo", "prioridad": "Alta", "descripcion": ""}
    )
    assert r1.status_code == 400

    # Intentar actualizar sin tipo
    r2 = authenticated_client.put(
        f"/ordenes/api/{orden_id}", json={"prioridad": "Alta", "descripcion": "Desc"}
    )
    assert r2.status_code == 400

    # Intentar actualizar sin prioridad
    r3 = authenticated_client.put(
        f"/ordenes/api/{orden_id}", json={"tipo": "Correctivo", "descripcion": "Desc"}
    )
    assert r3.status_code == 400


def test_actualizar_orden_fecha_programada_invalida(authenticated_client):
    orden_id = _crear_orden(authenticated_client, descripcion="Fecha inválida")
    resp = authenticated_client.put(
        f"/ordenes/api/{orden_id}", json={"tipo": "Preventivo", "prioridad": "Media", "descripcion": "x", "fecha_programada": "2024-13-40"}
    )
    assert resp.status_code == 400