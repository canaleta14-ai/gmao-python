import pytest


def test_dashboard_estadisticas_requires_auth(client):
    """El endpoint del dashboard debe requerir autenticación."""
    resp = client.get("/api/estadisticas", follow_redirects=False)
    # Redirige a login (302) o bloquea (401/403) según configuración
    assert resp.status_code in [302, 401, 403]


def test_dashboard_estadisticas_authenticated(authenticated_client):
    """Con usuario autenticado, el endpoint devuelve 200 y estructura mínima."""
    resp = authenticated_client.get("/api/estadisticas", follow_redirects=False)
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    # Claves mínimas garantizadas por el endpoint
    for key in [
        "ordenes_por_estado",
        "ordenes_ultima_semana",
        "activos_por_estado",
        "total_activos",
    ]:
        assert key in data


def test_planes_estadisticas_requires_auth(client):
    """El endpoint de estadísticas de planes debe requerir autenticación."""
    resp = client.get("/planes/api/estadisticas", follow_redirects=False)
    assert resp.status_code in [302, 401, 403]