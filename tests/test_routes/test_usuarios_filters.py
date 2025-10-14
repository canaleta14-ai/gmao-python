"""
Tests de filtros para listado de usuarios
"""


def test_usuarios_api_filters_authenticated(authenticated_client):
    # Probar múltiples filtros: q, rol, cargo, estado
    resp = authenticated_client.get(
        "/usuarios/api?q=test&rol=Técnico&cargo=Técnico&estado=Activo"
    )
    assert resp.status_code == 200
    data = resp.get_json()
    # El endpoint devuelve un objeto con metadata y lista de usuarios
    assert isinstance(data, dict)
    assert "usuarios" in data
    assert isinstance(data["usuarios"], list)