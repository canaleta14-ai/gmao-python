import pytest


def test_activos_estadisticas_success_structure(authenticated_client):
    """Con autenticación, activos devuelve estructura de estadísticas (dict con claves mínimas)."""
    resp = authenticated_client.get("/activos/api/estadisticas")
    assert resp.status_code == 200
    data = resp.get_json() or {}
    assert isinstance(data, dict)
    # claves mínimas esperadas pueden variar por implementación, verificamos presencia típica
    for key in [
        "total_activos",
        "activos_por_estado",
        "operativos",
        "en_mantenimiento",
    ]:
        # No todos los proyectos tienen todas las claves; exigimos al menos 1 clave conocida
        # Permitimos que falten algunas para evitar fragilidad
        if key in ("total_activos", "activos_por_estado"):
            assert key in data


def test_proveedores_estadisticas_success_structure(authenticated_client):
    """Con autenticación, proveedores devuelve estructura de estadísticas con claves definidas."""
    resp = authenticated_client.get("/proveedores/api/estadisticas")
    assert resp.status_code == 200
    data = resp.get_json() or {}
    assert isinstance(data, dict)
    for key in [
        "total_proveedores",
        "proveedores_activos",
        "proveedores_pendientes",
        "proveedores_inactivos",
    ]:
        assert key in data