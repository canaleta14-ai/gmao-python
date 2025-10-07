import pytest


def test_solicitudes_admin_estadisticas_forbidden_non_admin(app, client, usuario_tecnico):
    """Un usuario no administrador debe obtener 403 en /admin/solicitudes/api/estadisticas."""
    # Iniciar sesión como técnico
    resp_login = client.post(
        "/login",
        json={"username": "tecnico_test", "password": "tecnico123"},
        headers={"Content-Type": "application/json"},
    )
    assert resp_login.status_code in [200, 302]

    # Acceder al endpoint protegido
    resp = client.get("/admin/solicitudes/api/estadisticas", follow_redirects=False)
    assert resp.status_code == 403


def test_solicitudes_admin_estadisticas_admin_ok(authenticated_client):
    """Con usuario administrador, el endpoint devuelve 200 y estructura esperada."""
    resp = authenticated_client.get(
        "/admin/solicitudes/api/estadisticas", follow_redirects=False
    )
    assert resp.status_code == 200
    data = resp.get_json()
    for key in [
        "total",
        "pendientes",
        "en_progreso",
        "completadas",
        "tipos",
        "prioridades",
    ]:
        assert key in data