import pytest


@pytest.mark.parametrize(
    "path",
    [
        "/ordenes/estadisticas",
        "/ordenes/activos",
        "/ordenes/tecnicos",
        "/activos/api/estadisticas",
        "/inventario/api/estadisticas",
        "/planes/api/estadisticas",
        "/proveedores/api/estadisticas",
    ],
)
def test_protected_endpoints_require_auth(client, path):
    """Todas estas rutas deben requerir autenticación."""
    resp = client.get(path, follow_redirects=False)
    assert resp.status_code in [302, 401, 403]


def test_categorias_estadisticas_public_ok_or_missing(client):
    """La ruta puede responder 200 (si está registrada) o 404 (si no)."""
    resp = client.get("/categorias/estadisticas")
    assert resp.status_code in [200, 404]
    if resp.status_code == 200:
        data = resp.get_json() or {}
        assert data.get("success") is True
        assert "total_categorias" in data
        assert "categorias_top" in data