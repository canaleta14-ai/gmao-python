"""
Smoke tests mínimos para endpoints core autenticados.

Estos tests validan que las rutas principales responden bajo autenticación
y devuelven JSON estructurado básico. Son tolerantes con la forma exacta.
"""


def test_activos_api_authenticated(authenticated_client):
    resp = authenticated_client.get("/activos/api")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data is not None


def test_inventario_api_authenticated(authenticated_client):
    resp = authenticated_client.get("/inventario/api")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data is not None


def test_proveedores_api_authenticated(authenticated_client):
    resp = authenticated_client.get("/proveedores/api")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data is not None