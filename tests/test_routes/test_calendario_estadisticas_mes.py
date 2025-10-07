import pytest
from datetime import datetime


def test_calendario_estadisticas_mes_success(authenticated_client):
    """Comprueba que /calendario/api/estadisticas-mes responde 200 y estructura esperada."""
    now = datetime.now()
    resp = authenticated_client.get(
        f"/calendario/api/estadisticas-mes?year={now.year}&month={now.month}",
        follow_redirects=False,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("success") is True
    assert isinstance(data.get("ordenes_por_estado"), dict)
    assert isinstance(data.get("total_ordenes"), int)
    assert isinstance(data.get("planes_programados"), int)
    assert isinstance(data.get("mes_nombre"), str)
    assert isinstance(data.get("anio"), int)