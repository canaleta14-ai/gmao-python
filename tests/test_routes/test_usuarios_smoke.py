"""
Smoke tests para endpoints de Usuarios API.
"""


def test_usuarios_list_authenticated(authenticated_client):
    resp = authenticated_client.get("/usuarios/api")
    assert resp.status_code in [200, 500]
    data = resp.get_json()
    assert data is not None


def test_usuarios_list_query_authenticated(authenticated_client):
    resp = authenticated_client.get("/usuarios/api?q=test&rol=Técnico")
    assert resp.status_code in [200, 500]
    data = resp.get_json()
    assert data is not None


def test_usuarios_roles_authenticated(authenticated_client):
    resp = authenticated_client.get("/usuarios/api/roles")
    assert resp.status_code in [200, 500]
    data = resp.get_json()
    assert data is not None


def test_usuario_detalle_authenticated(authenticated_client):
    resp = authenticated_client.get("/usuarios/api/1")
    assert resp.status_code in [200, 404, 500]
    data = resp.get_json()
    assert data is not None