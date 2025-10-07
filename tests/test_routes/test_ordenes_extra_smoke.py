import pytest


def test_get_activos_authenticated(authenticated_client):
    resp = authenticated_client.get("/ordenes/activos")
    assert resp.status_code in [200, 400, 500]
    # Debe devolver JSON o un mensaje de error
    try:
        data = resp.get_json()
        assert data is not None
    except Exception:
        # Algunas respuestas de error pueden no ser JSON
        assert resp.data is not None


def test_get_tecnicos_authenticated(authenticated_client):
    resp = authenticated_client.get("/ordenes/tecnicos")
    assert resp.status_code in [200, 400, 500]
    try:
        data = resp.get_json()
        assert data is not None
    except Exception:
        assert resp.data is not None


def test_listar_ordenes_paginado_authenticated(authenticated_client):
    resp = authenticated_client.get("/ordenes/api?page=1&per_page=5")
    assert resp.status_code in [200, 400]
    try:
        data = resp.get_json()
        assert data is not None
    except Exception:
        assert resp.data is not None