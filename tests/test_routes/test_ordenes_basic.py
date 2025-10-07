import pytest


def test_ordenes_page_requires_auth(client):
    response = client.get("/ordenes/", follow_redirects=False)
    assert response.status_code in [302, 401, 403]


def test_ordenes_page_authenticated_ok(authenticated_client):
    response = authenticated_client.get("/ordenes/")
    assert response.status_code == 200
    assert "text/html" in response.content_type


def test_listar_ordenes_api_basic(authenticated_client):
    # Listado tradicional sin paginación
    response = authenticated_client.get("/ordenes/api?limit=1")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_listar_ordenes_api_paginado(authenticated_client):
    # Listado con paginación
    response = authenticated_client.get("/ordenes/api?page=1&per_page=2")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, dict)
    # Validar estructura mínima del paginado
    for key in ["items", "page", "per_page", "total"]:
        assert key in data


def test_crear_actualizar_eliminar_orden_flow(authenticated_client):
    # Crear orden mínima
    payload = {
        "tipo": "Correctivo",
        "prioridad": "Media",
        "descripcion": "Orden de prueba cobertura",
    }
    resp_create = authenticated_client.post("/ordenes/", json=payload)
    assert resp_create.status_code in [201, 200]
    data_create = resp_create.get_json() or {}
    # Tolerar estructura variable
    orden_id = data_create.get("id")
    assert orden_id is not None

    # Actualizar estado válido
    resp_estado = authenticated_client.put(
        f"/ordenes/api/{orden_id}/estado", json={"estado": "En Proceso"}
    )
    assert resp_estado.status_code == 200

    # Obtener detalles de la orden
    resp_get = authenticated_client.get(f"/ordenes/api/{orden_id}")
    assert resp_get.status_code == 200
    data_get = resp_get.get_json()
    assert isinstance(data_get, dict)
    assert data_get.get("id") == orden_id

    # Eliminar la orden creada
    resp_del = authenticated_client.delete(f"/ordenes/api/{orden_id}")
    assert resp_del.status_code == 200


def test_actualizar_estado_invalido(authenticated_client):
    # Crear orden para probar estado inválido
    payload = {
        "tipo": "Preventivo",
        "prioridad": "Baja",
        "descripcion": "Orden para estado inválido",
    }
    resp_create = authenticated_client.post("/ordenes/", json=payload)
    assert resp_create.status_code in [201, 200]
    orden_id = (resp_create.get_json() or {}).get("id")
    assert orden_id is not None

    # Intentar actualizar a un estado inválido
    resp_estado = authenticated_client.put(
        f"/ordenes/api/{orden_id}/estado", json={"estado": "Desconocido"}
    )
    assert resp_estado.status_code == 400