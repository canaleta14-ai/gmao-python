"""
Smoke tests para páginas principales de la aplicación.

Estos tests verifican que las vistas principales cargan con autenticación.
"""


def test_ordenes_page(authenticated_client):
    resp = authenticated_client.get("/ordenes/")
    assert resp.status_code == 200


def test_usuarios_page(authenticated_client):
    resp = authenticated_client.get("/usuarios/")
    assert resp.status_code == 200


def test_proveedores_page(authenticated_client):
    resp = authenticated_client.get("/proveedores/")
    assert resp.status_code == 200


def test_recambios_page(authenticated_client):
    resp = authenticated_client.get("/recambios/")
    assert resp.status_code == 200


def test_planes_page(authenticated_client):
    resp = authenticated_client.get("/planes/")
    assert resp.status_code == 200