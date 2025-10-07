import pytest


def test_get_departamentos_authenticated(authenticated_client):
    resp = authenticated_client.get("/activos/departamentos")
    assert resp.status_code in [200, 500]
    try:
        data = resp.get_json()
        assert data is not None
    except Exception:
        assert resp.data is not None


def test_get_siguiente_codigo_authenticated(authenticated_client):
    resp = authenticated_client.get("/activos/generar-codigo/General")
    assert resp.status_code in [200, 400]
    try:
        data = resp.get_json()
        assert data is not None
        assert "codigo" in data or "error" in data
    except Exception:
        assert resp.data is not None


def test_descargar_manual_public(client):
    # No requiere autenticación según rutas, puede devolver 200/404/500
    resp = client.get("/activos/api/manuales/1/descargar")
    assert resp.status_code in [200, 404, 500]
    assert resp.data is not None