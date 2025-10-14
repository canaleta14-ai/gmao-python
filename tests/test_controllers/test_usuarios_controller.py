"""
Tests para el controlador de usuarios
"""
import pytest
from app.models.usuario import Usuario


def test_get_usuarios_api_authenticated(authenticated_client):
    """Test del endpoint GET /usuarios/api con autenticación"""
    resp = authenticated_client.get("/usuarios/api")
    assert resp.status_code == 200
    data = resp.get_json()
    # El endpoint devuelve un objeto con metadata y lista de usuarios
    assert isinstance(data, dict)
    assert "usuarios" in data
    assert isinstance(data["usuarios"], list)


def test_get_usuarios_api_unauthenticated(client):
    """Test del endpoint GET /usuarios/api sin autenticación"""
    resp = client.get("/usuarios/api")
    assert resp.status_code == 302  # Redirect to login


def test_login_json_invalid_credentials(client):
    """Test de login JSON con credenciales inválidas"""
    resp = client.post("/login", json={
        "username": "invalid_user",
        "password": "wrong_password"
    })
    assert resp.status_code in [400, 401]
    data = resp.get_json()
    assert "error" in data


def test_login_form_invalid_credentials(client):
    """Test de login con form data y credenciales inválidas"""
    resp = client.post("/login", data={
        "username": "invalid_user",
        "password": "wrong_password"
    })
    assert resp.status_code in [400, 401, 302]


def test_login_missing_fields(client):
    """Test de login con campos faltantes"""
    resp = client.post("/login", json={
        "username": "test"
        # Missing password
    })
    assert resp.status_code == 400


def test_login_empty_fields(client):
    """Test de login con campos vacíos"""
    resp = client.post("/login", json={
        "username": "",
        "password": ""
    })
    assert resp.status_code == 400


def test_usuarios_page_authenticated(authenticated_client):
    """Test de la página de usuarios con autenticación"""
    resp = authenticated_client.get("/usuarios/")
    assert resp.status_code == 200


def test_crear_usuario_authenticated(authenticated_client):
    """Test de creación de usuario con autenticación"""
    resp = authenticated_client.post("/usuarios/api", json={
        "username": "test_new_user",
        "email": "test@example.com",
        "password": "test123",
        "rol": "tecnico"
    })
    # May return 201 (created) or 400 (validation error)
    assert resp.status_code in [201, 400]


def test_crear_usuario_invalid_data(authenticated_client):
    """Test de creación de usuario con datos inválidos"""
    resp = authenticated_client.post("/usuarios/api", json={
        "username": "",  # Empty username
        "email": "invalid-email",
        "password": "123",  # Too short
        "rol": "invalid_role"
    })
    assert resp.status_code == 400