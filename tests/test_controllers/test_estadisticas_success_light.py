import pytest


def test_dashboard_estadisticas_controller_success(app):
    """El controlador de estadísticas del dashboard devuelve estructura mínima válida."""
    from app.controllers.estadisticas_controller import obtener_estadisticas

    with app.app_context():
        data = obtener_estadisticas()
        assert isinstance(data, dict)
        for key in [
            "ordenes_por_estado",
            "ordenes_ultima_semana",
            "activos_por_estado",
            "total_activos",
        ]:
            assert key in data


def test_planes_controller_obtener_estadisticas_keys(app):
    """El controlador de planes devuelve las claves esperadas."""
    from app.controllers.planes_controller import obtener_estadisticas_planes

    with app.app_context():
        stats = obtener_estadisticas_planes()
        assert isinstance(stats, dict)
        for key in [
            "planes_activos",
            "planes_proximos",
            "planes_vencidos",
            "planes_completados",
            "total_planes",
        ]:
            assert key in stats


def test_ordenes_controller_obtener_estadisticas_keys(app):
    """El controlador de órdenes devuelve las claves esperadas."""
    from app.controllers.ordenes_controller import obtener_estadisticas_ordenes

    with app.app_context():
        stats = obtener_estadisticas_ordenes()
        assert isinstance(stats, dict)
        for key in [
            "por_estado",
            "ordenes_semana",
            "ordenes_vencidas",
            "tiempo_promedio_resolucion",
        ]:
            assert key in stats


def test_inventario_controller_obtener_estadisticas_keys(app):
    """El controlador de inventario devuelve las claves esperadas."""
    from app.controllers.inventario_controller import obtener_estadisticas_inventario

    with app.app_context():
        stats = obtener_estadisticas_inventario()
        assert isinstance(stats, dict)
        for key in [
            "total_articulos",
            "articulos_bajo_minimo",
            "valor_total_inventario",
            "articulos_criticos",
            "movimientos_mes",
        ]:
            assert key in stats