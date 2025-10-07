import pytest


def test_dashboard_estadisticas_fallback_on_error(authenticated_client, monkeypatch):
    """Si el controlador lanza error, el endpoint debe devolver 200 con estructura por defecto."""
    import app.routes.estadisticas as estadisticas_routes

    def raise_exc():
        raise Exception("boom")

    monkeypatch.setattr(estadisticas_routes, "obtener_estadisticas", raise_exc)

    resp = authenticated_client.get("/api/estadisticas", follow_redirects=False)
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    for key in [
        "ordenes_por_estado",
        "ordenes_ultima_semana",
        "activos_por_estado",
        "total_activos",
    ]:
        assert key in data


def test_dashboard_estadisticas_success_min_structure(authenticated_client):
    """Con autenticación, el endpoint devuelve 200 y claves mínimas aseguradas."""
    resp = authenticated_client.get("/api/estadisticas", follow_redirects=False)
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    for key in [
        "ordenes_por_estado",
        "ordenes_ultima_semana",
        "activos_por_estado",
        "total_activos",
    ]:
        assert key in data