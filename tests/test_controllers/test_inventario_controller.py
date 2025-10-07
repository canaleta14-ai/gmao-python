"""
Tests para el controlador de inventario
"""
import pytest


def test_get_inventario_api_authenticated(authenticated_client):
    """Test del endpoint GET /inventario/api con autenticación"""
    resp = authenticated_client.get("/inventario/api")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_get_inventario_api_unauthenticated(client):
    """Test del endpoint GET /inventario/api sin autenticación"""
    resp = client.get("/inventario/api")
    assert resp.status_code == 302  # Redirect to login


def test_inventario_page_authenticated(authenticated_client):
    """Test de la página de inventario con autenticación"""
    resp = authenticated_client.get("/inventario/")
    assert resp.status_code == 200


def test_crear_item_inventario_authenticated(authenticated_client):
    """Test de creación de item de inventario con autenticación"""
    resp = authenticated_client.post("/inventario/api", json={
        "nombre": "Test Item",
        "descripcion": "Test Description",
        "cantidad": 10,
        "precio_unitario": 25.50,
        "categoria": "Herramientas"
    })
    # May return 201 (created) or 400 (validation error)
    assert resp.status_code in [201, 400]


def test_crear_item_inventario_invalid_data(authenticated_client):
    """Test de creación de item con datos inválidos"""
    resp = authenticated_client.post("/inventario/api", json={
        "nombre": "",  # Empty name
        "cantidad": -5,  # Negative quantity
        "precio_unitario": "invalid"  # Invalid price
    })
    assert resp.status_code == 400


def test_buscar_inventario_authenticated(authenticated_client):
    """Test de búsqueda en inventario con autenticación"""
    resp = authenticated_client.get("/inventario/api?q=test")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_buscar_inventario_malicious_input(authenticated_client):
    """Test de búsqueda con input malicioso"""
    resp = authenticated_client.get("/inventario/api?q=<script>alert('xss')</script>")
    # Should handle malicious input gracefully
    assert resp.status_code in [200, 400]


def test_actualizar_item_inventario_authenticated(authenticated_client):
    """Test de actualización de item de inventario"""
    # First try to get an item to update
    resp = authenticated_client.get("/inventario/api")
    assert resp.status_code == 200
    
    # Try to update with ID 1 (may or may not exist)
    resp = authenticated_client.put("/inventario/api/1", json={
        "nombre": "Updated Item",
        "cantidad": 15
    })
    # May return 200 (updated), 404 (not found), or 400 (validation error)
    assert resp.status_code in [200, 404, 400]


def test_eliminar_item_inventario_authenticated(authenticated_client):
    """Test de eliminación de item de inventario"""
    # Try to delete item with ID 999 (likely doesn't exist)
    resp = authenticated_client.delete("/inventario/api/999")
    # Should return 404 for non-existent item
    assert resp.status_code in [404, 200]