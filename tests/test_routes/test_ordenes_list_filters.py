"""
Tests de filtros para listado de órdenes de trabajo
"""


def test_listar_ordenes_paginado_authenticated(authenticated_client):
    resp = authenticated_client.get(
        "/ordenes/api?page=1&per_page=2&q=test&estado=Pendiente&tipo=Correctivo&prioridad=Media"
    )
    assert resp.status_code == 200
    data = resp.get_json()
    # Debe ser un dict con paginación
    assert isinstance(data, dict)
    assert "items" in data
    assert "page" in data


def test_listar_ordenes_limit_authenticated(authenticated_client):
    resp = authenticated_client.get("/ordenes/api?limit=5")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)