import pytest


def test_crear_orden_missing_tipo_returns_400(authenticated_client):
    resp = authenticated_client.post("/ordenes/", json={})
    assert resp.status_code == 400
    data = resp.get_json() or {}
    assert data.get("error") == "El tipo es requerido"


def test_crear_orden_missing_prioridad_returns_400(authenticated_client):
    payload = {"tipo": "Correctivo"}
    resp = authenticated_client.post("/ordenes/", json=payload)
    assert resp.status_code == 400
    data = resp.get_json() or {}
    assert data.get("error") == "La prioridad es requerida"


def test_crear_orden_missing_descripcion_returns_400(authenticated_client):
    payload = {"tipo": "Correctivo", "prioridad": "Alta"}
    resp = authenticated_client.post("/ordenes/", json=payload)
    assert resp.status_code == 400
    data = resp.get_json() or {}
    assert data.get("error") == "La descripción es requerida"


def test_actualizar_estado_missing_returns_400(authenticated_client):
    # Crear una orden válida primero
    payload = {
        "tipo": "Preventivo",
        "prioridad": "Media",
        "descripcion": "Orden para probar estado faltante",
    }
    resp_create = authenticated_client.post("/ordenes/", json=payload)
    assert resp_create.status_code in [200, 201]
    orden_id = (resp_create.get_json() or {}).get("id")
    assert orden_id is not None

    # Intentar actualizar estado sin enviar campo 'estado'
    resp_estado = authenticated_client.put(f"/ordenes/api/{orden_id}/estado", json={})
    assert resp_estado.status_code == 400
    data = resp_estado.get_json() or {}
    assert data.get("error") == "El estado es requerido"


def test_eliminar_orden_completada_returns_400(authenticated_client):
    # Crear una orden y marcarla como Completada
    payload = {
        "tipo": "Correctivo",
        "prioridad": "Baja",
        "descripcion": "Orden completada no debe eliminarse",
    }
    resp_create = authenticated_client.post("/ordenes/", json=payload)
    assert resp_create.status_code in [200, 201]
    orden_id = (resp_create.get_json() or {}).get("id")
    assert orden_id is not None

    # Cambiar estado a Completada
    resp_estado = authenticated_client.put(
        f"/ordenes/api/{orden_id}/estado", json={"estado": "Completada"}
    )
    assert resp_estado.status_code in [200, 400]

    # Intentar eliminar y esperar 400
    resp_del = authenticated_client.delete(f"/ordenes/api/{orden_id}")
    assert resp_del.status_code == 400
    data = resp_del.get_json() or {}
    assert "error" in data