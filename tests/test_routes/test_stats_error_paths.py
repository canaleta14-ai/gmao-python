import pytest


def test_activos_estadisticas_error_returns_500(authenticated_client, monkeypatch):
    """Simular error en controlador para verificar respuesta 500 en /activos/api/estadisticas."""
    import app.routes.activos as activos_routes

    def raise_exc():
        raise Exception("fail")

    monkeypatch.setattr(activos_routes, "obtener_estadisticas_activos", raise_exc)

    resp = authenticated_client.get("/activos/api/estadisticas", follow_redirects=False)
    assert resp.status_code == 500
    data = resp.get_json() or {}
    assert "error" in data


def test_inventario_estadisticas_error_returns_500(authenticated_client, monkeypatch):
    """Simular error en controlador para verificar respuesta 500 en /inventario/api/estadisticas."""
    import app.routes.inventario as inventario_routes

    def raise_exc():
        raise Exception("boom")

    monkeypatch.setattr(
        inventario_routes, "obtener_estadisticas_inventario", raise_exc
    )

    resp = authenticated_client.get(
        "/inventario/api/estadisticas", follow_redirects=False
    )
    assert resp.status_code == 500
    data = resp.get_json() or {}
    assert data.get("success") is False
    assert "error" in data