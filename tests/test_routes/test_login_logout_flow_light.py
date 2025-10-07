import pytest


def test_login_get_authenticated_redirects(authenticated_client):
    """Acceder a /login autenticado debe redirigir al dashboard."""
    resp = authenticated_client.get("/login")
    assert resp.status_code in [302, 301]
    location = resp.headers.get("Location", "")
    assert "dashboard" in location


def test_logout_requires_auth(client):
    """/logout debe requerir autenticación."""
    resp = client.get("/logout", follow_redirects=False)
    assert resp.status_code in [302, 401, 403]


def test_logout_authenticated_redirects_to_login(authenticated_client):
    """Con autenticación, /logout debe cerrar sesión y redirigir a /login."""
    resp = authenticated_client.get("/logout")
    assert resp.status_code in [302, 301]
    location = resp.headers.get("Location", "")
    assert "login" in location