"""
Smoke tests para endpoints de Inventario API.
"""


def test_inventario_list_alias_authenticated(authenticated_client):
    resp = authenticated_client.get("/inventario/api")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data is not None


def test_inventario_articulos_authenticated(authenticated_client):
    resp = authenticated_client.get("/inventario/api/articulos")
    assert resp.status_code in [200, 400]
    data = resp.get_json()
    assert data is not None


def test_inventario_conteos_authenticated(authenticated_client):
    resp = authenticated_client.get("/inventario/api/conteos")
    assert resp.status_code in [200, 400]
    data = resp.get_json()
    assert data is not None


def test_inventario_conteos_resumen_authenticated(authenticated_client):
    resp = authenticated_client.get("/inventario/api/conteos/resumen")
    assert resp.status_code in [200, 400]
    data = resp.get_json()
    assert data is not None


def test_inventario_periodos_authenticated(authenticated_client):
    resp = authenticated_client.get("/inventario/api/periodos-inventario")
    assert resp.status_code in [200, 400]
    data = resp.get_json()
    assert data is not None