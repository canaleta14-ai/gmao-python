import pytest


def test_login_page_accessible(client):
    resp = client.get("/login")
    assert resp.status_code == 200


def test_login_invalid_payload_returns_400(client):
    resp = client.post(
        "/login",
        json={"username": "", "password": ""},
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data.get("success") is False


def test_login_valid_returns_success(authenticated_client):
    resp = authenticated_client.post(
        "/login",
        json={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code in [200, 302]
    data = resp.get_json()
    assert data.get("success") in [True, 1, "true"]


def test_usuarios_protected_requires_auth(client):
    resp = client.get("/usuarios/")
    assert resp.status_code in [302, 401, 403]


def test_usuarios_page_after_login(authenticated_client):
    resp = authenticated_client.get("/usuarios/")
    assert resp.status_code == 200


def test_usuarios_api_authenticated(authenticated_client):
    resp = authenticated_client.get("/usuarios/api")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("success") is True
    assert isinstance(data.get("usuarios"), list)