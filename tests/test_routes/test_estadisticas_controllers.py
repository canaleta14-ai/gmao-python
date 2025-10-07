import pytest


def test_dashboard_estadisticas_error_fallback_authenticated(authenticated_client, monkeypatch):
    """Si el controlador lanza excepción, el endpoint del dashboard devuelve 200 con estructura por defecto."""

    # Forzar excepción en el controlador
    from app.controllers import estadisticas_controller as ec

    def _raise(*args, **kwargs):
        raise Exception("boom")

    monkeypatch.setattr(ec, "obtener_estadisticas", _raise)

    resp = authenticated_client.get("/api/estadisticas")
    assert resp.status_code == 200
    data = resp.get_json()
    # Estructura mínima esperada
    for key in [
        "ordenes_por_estado",
        "ordenes_ultima_semana",
        "activos_por_estado",
        "total_activos",
    ]:
        assert key in data


def test_ordenes_estadisticas_error_returns_500(authenticated_client, monkeypatch):
    """Si el controlador de órdenes falla, la ruta debe responder 500 con mensaje de error."""
    import app.routes.ordenes as ordenes_routes

    def _raise(*args, **kwargs):
        raise Exception("boom")

    monkeypatch.setattr(ordenes_routes, "obtener_estadisticas_ordenes", _raise)

    resp = authenticated_client.get("/ordenes/estadisticas")
    assert resp.status_code == 500
    data = resp.get_json() or {}
    assert "error" in data


def test_planes_estadisticas_success_structure(authenticated_client):
    """Con autenticación, planes devuelve estructura con success=True y objeto estadisticas."""
    resp = authenticated_client.get("/planes/api/estadisticas")
    assert resp.status_code == 200
    data = resp.get_json() or {}
    assert data.get("success") is True
    assert isinstance(data.get("estadisticas", {}), dict)


def test_planes_estadisticas_error_returns_500(authenticated_client, monkeypatch):
    """Si falla el controlador de planes, debe responder 500 con success=False."""
    import app.routes.planes as planes_routes

    def _raise(*args, **kwargs):
        raise Exception("boom")

    monkeypatch.setattr(planes_routes, "obtener_estadisticas_planes", _raise)

    resp = authenticated_client.get("/planes/api/estadisticas")
    assert resp.status_code == 500
    data = resp.get_json() or {}
    assert data.get("success") is False
    assert "error" in data


def test_inventario_estadisticas_error_returns_500(authenticated_client, monkeypatch):
    """Error en controlador de inventario debe dar 500 y success=False."""
    import app.routes.inventario as inventario_routes

    def _raise(*args, **kwargs):
        raise Exception("boom")

    monkeypatch.setattr(inventario_routes, "obtener_estadisticas_inventario", _raise)

    resp = authenticated_client.get("/inventario/api/estadisticas")
    assert resp.status_code == 500
    data = resp.get_json() or {}
    # La ruta devuelve success False en error
    assert data.get("success") is False
    assert "error" in data


def test_activos_estadisticas_error_returns_500(authenticated_client, monkeypatch):
    """Error en controlador de activos debe responder 500 con mensaje de error."""
    import app.routes.activos as activos_routes

    def _raise(*args, **kwargs):
        raise Exception("boom")

    monkeypatch.setattr(activos_routes, "obtener_estadisticas_activos", _raise)

    resp = authenticated_client.get("/activos/api/estadisticas")
    assert resp.status_code == 500
    data = resp.get_json() or {}
    assert "error" in data


def test_proveedores_estadisticas_error_returns_500(authenticated_client, monkeypatch):
    """Error en controlador de proveedores debe responder 500 con mensaje de error."""
    import app.routes.proveedores as proveedores_routes

    def _raise(*args, **kwargs):
        raise Exception("boom")

    monkeypatch.setattr(proveedores_routes, "obtener_estadisticas_proveedores", _raise)

    resp = authenticated_client.get("/proveedores/api/estadisticas")
    assert resp.status_code == 500
    data = resp.get_json() or {}
    assert "error" in data