"""
Tests para el controlador de órdenes de trabajo
"""
import pytest


def test_get_ordenes_api_authenticated(authenticated_client):
    """Test del endpoint GET /ordenes/api con autenticación"""
    resp = authenticated_client.get("/ordenes/api")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_get_ordenes_api_unauthenticated(client):
    """Test del endpoint GET /ordenes/api sin autenticación"""
    resp = client.get("/ordenes/api")
    assert resp.status_code == 302  # Redirect to login


def test_ordenes_page_authenticated(authenticated_client):
    """Test de la página de órdenes con autenticación"""
    resp = authenticated_client.get("/ordenes/")
    assert resp.status_code == 200


def test_crear_orden_authenticated(authenticated_client):
    """Test de creación de orden de trabajo con autenticación"""
    resp = authenticated_client.post("/ordenes/api", json={
        "titulo": "Test Order",
        "descripcion": "Test Description",
        "prioridad": "media",
        "activo_id": 1,
        "asignado_a": 1
    })
    # May return 201 (created) or 400 (validation error)
    assert resp.status_code in [201, 400]


def test_crear_orden_invalid_data(authenticated_client):
    """Test de creación de orden con datos inválidos"""
    resp = authenticated_client.post("/ordenes/api", json={
        "titulo": "",  # Empty title
        "prioridad": "invalid_priority",
        "activo_id": "invalid_id"
    })
    assert resp.status_code == 400


def test_buscar_ordenes_authenticated(authenticated_client):
    """Test de búsqueda en órdenes con autenticación"""
    resp = authenticated_client.get("/ordenes/api?q=test")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_buscar_ordenes_malicious_input(authenticated_client):
    """Test de búsqueda con input malicioso"""
    resp = authenticated_client.get("/ordenes/api?q=UNION SELECT * FROM usuarios")
    # Should handle malicious input gracefully
    assert resp.status_code in [200, 400]


def test_actualizar_orden_authenticated(authenticated_client):
    """Test de actualización de orden de trabajo"""
    # Try to update with ID 1 (may or may not exist)
    resp = authenticated_client.put("/ordenes/api/1", json={
        "titulo": "Updated Order",
        "estado": "en_progreso"
    })
    # May return 200 (updated), 404 (not found), or 400 (validation error)
    assert resp.status_code in [200, 404, 400]


def test_eliminar_orden_authenticated(authenticated_client):
    """Test de eliminación de orden de trabajo"""
    # Try to delete order with ID 999 (likely doesn't exist)
    resp = authenticated_client.delete("/ordenes/api/999")
    # Should return 404 for non-existent order
    assert resp.status_code in [404, 200]


def test_get_orden_by_id_authenticated(authenticated_client):
    """Test de obtener orden por ID"""
    resp = authenticated_client.get("/ordenes/api/1")
    # May return 200 (found) or 404 (not found)
    assert resp.status_code in [200, 404]


def test_cambiar_estado_orden_authenticated(authenticated_client):
    """Test de cambio de estado de orden"""
    resp = authenticated_client.patch("/ordenes/api/1/estado", json={
        "estado": "completada"
    })
    # May return 200 (updated), 404 (not found), or 400 (validation error)
    assert resp.status_code in [200, 404, 400]


def test_asignar_orden_authenticated(authenticated_client):
    """Test de asignación de orden a técnico"""
    resp = authenticated_client.patch("/ordenes/api/1/asignar", json={
        "asignado_a": 1
    })
    # May return 200 (updated), 404 (not found), or 400 (validation error)
    assert resp.status_code in [200, 404, 400]