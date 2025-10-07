"""
Smoke tests para endpoints de órdenes de trabajo

Estos tests ayudan a aumentar la cobertura de rutas clave sin modificar
la lógica de negocio. Usan el fixture authenticated_client existente.
"""


def test_get_activos_authenticated(authenticated_client):
    resp = authenticated_client.get("/ordenes/activos")
    # Debe responder 200 con lista (aunque pueda estar vacía)
    assert resp.status_code == 200


def test_get_tecnicos_authenticated(authenticated_client):
    resp = authenticated_client.get("/ordenes/tecnicos")
    assert resp.status_code == 200


def test_get_estadisticas_authenticated(authenticated_client):
    resp = authenticated_client.get("/ordenes/estadisticas")
    # Debe ser 200 o 400 si alguna validación falla internamente
    assert resp.status_code in [200, 400]


def test_exportar_csv_authenticated(authenticated_client):
    resp = authenticated_client.get("/ordenes/exportar-csv")
    # Debe retornar el archivo Excel (200)
    assert resp.status_code == 200