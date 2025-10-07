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
    assert isinstance(data, list)