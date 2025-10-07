import pytest


def test_health_unhealthy_on_db_error(client, monkeypatch):
    """Si falla la consulta a la BD, /health debe responder 503 con status 'unhealthy'."""
    import app.routes.web as web_routes

    def _raise(*args, **kwargs):
        raise Exception("db down")

    # Forzar fallo en la verificación de BD
    monkeypatch.setattr(web_routes.db.session, "execute", _raise)

    resp = client.get("/health")
    assert resp.status_code == 503
    data = resp.get_json() or {}
    assert data.get("status") == "unhealthy"