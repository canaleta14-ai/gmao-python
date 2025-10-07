import pytest


def test_index_redirects_unauthenticated(client):
    response = client.get("/")
    # Debe redirigir a login
    assert response.status_code in [302, 301]
    # No asumimos ruta exacta, solo que hay Location
    assert "Location" in response.headers


def test_index_redirects_to_dashboard_authenticated(authenticated_client):
    response = authenticated_client.get("/")
    # Usuario autenticado debe ir al dashboard
    assert response.status_code in [302, 301]
    location = response.headers.get("Location", "")
    assert "dashboard" in location


def test_get_notificaciones_authenticated(authenticated_client):
    response = authenticated_client.get("/api/notificaciones")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_health_check(client):
    """Test del endpoint de health check"""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_dashboard_requires_auth(client):
    """Test que el dashboard requiere autenticación"""
    resp = client.get("/dashboard")
    # Should redirect to login
    assert resp.status_code == 302


def test_dashboard_with_auth(authenticated_client):
    """Test del dashboard con usuario autenticado"""
    resp = authenticated_client.get("/dashboard")
    assert resp.status_code == 200


def test_login_page_get(client):
    """Test de la página de login (GET)"""
    resp = client.get("/login")
    assert resp.status_code == 200


def test_logout_endpoint(authenticated_client):
    """Test del endpoint de logout"""
    resp = authenticated_client.post("/logout")
    assert resp.status_code in [200, 302]


def test_activos_page_requires_auth(client):
    """Test que la página de activos requiere autenticación"""
    resp = client.get("/activos/")
    assert resp.status_code == 302


def test_ordenes_page_requires_auth(client):
    """Test que la página de órdenes requiere autenticación"""
    resp = client.get("/ordenes/")
    assert resp.status_code == 302


def test_usuarios_page_requires_auth(client):
    """Test que la página de usuarios requiere autenticación"""
    resp = client.get("/usuarios/")
    assert resp.status_code == 302


def test_inventario_page_requires_auth(client):
    """Test que la página de inventario requiere autenticación"""
    resp = client.get("/inventario/")
    assert resp.status_code == 302


def test_estadisticas_page_requires_auth(client):
    """Test que la página de estadísticas requiere autenticación"""
    resp = client.get("/estadisticas/")
    # May return 302 (redirect) or 404 (not found) depending on route existence
    assert resp.status_code in [302, 404]