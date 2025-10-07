"""
Smoke tests para endpoints de planes de mantenimiento.

Verifican respuestas básicas bajo autenticación.
"""


def test_planes_api_list_authenticated(authenticated_client):
    resp = authenticated_client.get("/planes/api")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data is not None


def test_plan_individual_not_found_or_ok(authenticated_client):
    resp = authenticated_client.get("/planes/api/999999")
    assert resp.status_code in [200, 404]
    data = resp.get_json()
    assert data is not None


def test_generar_ordenes_post_authenticated(authenticated_client):
    resp = authenticated_client.post("/planes/generar-ordenes", json={})
    assert resp.status_code in [200, 400, 500]
    data = resp.get_json()
    assert data is not None


def test_generar_ordenes_manual_authenticated(authenticated_client):
    resp = authenticated_client.post("/planes/api/generar-ordenes-manual")
    assert resp.status_code in [200, 500]
    data = resp.get_json()
    assert data is not None