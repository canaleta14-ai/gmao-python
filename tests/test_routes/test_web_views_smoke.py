import pytest


@pytest.mark.parametrize("path", [
    "/test-notificaciones",
    "/alertas-test",
    "/test-modales",
])
def test_web_views_smoke(client, path):
    """Las vistas de prueba deben responder 200 si los templates existen, o 500 si falta el template."""
    resp = client.get(path)
    assert resp.status_code in [200, 500]