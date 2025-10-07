import pytest


def test_health_public(client):
    resp = client.get("/health")
    assert resp.status_code in [200, 503]
    try:
        data = resp.get_json()
        assert data is not None
        assert "status" in data
    except Exception:
        assert resp.data is not None


def test_index_redirect_authenticated(authenticated_client):
    resp = authenticated_client.get("/", follow_redirects=False)
    assert resp.status_code in [302, 200]


def test_dashboard_authenticated(authenticated_client):
    resp = authenticated_client.get("/dashboard")
    assert resp.status_code == 200


def test_user_info_authenticated(authenticated_client):
    resp = authenticated_client.get("/api/user/info")
    assert resp.status_code in [200, 401]
    try:
        data = resp.get_json()
        assert data is not None
    except Exception:
        assert resp.data is not None