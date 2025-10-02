"""
Tests unitarios para el modelo OrdenTrabajo
"""

import pytest
from datetime import datetime
from app.models.orden_trabajo import OrdenTrabajo


@pytest.mark.unit
class TestOrdenTrabajoModel:

    def test_crear_orden_basica(self, db_session, activo_test, usuario_tecnico):
        """Test creación básica de orden de trabajo"""
        orden = OrdenTrabajo(
            numero_orden="OT-2024-001",
            activo_id=activo_test.id,
            tecnico_id=usuario_tecnico.id,
            tipo="Preventivo",
            estado="Pendiente",
            descripcion="Test orden",
            prioridad="Media",
        )
        db_session.add(orden)
        db_session.commit()

        assert orden.id is not None
        assert orden.numero_orden == "OT-2024-001"
        assert orden.estado == "Pendiente"
        assert orden.tipo == "Preventivo"

    def test_orden_con_plan_mantenimiento(
        self, db_session, plan_mantenimiento_test, activo_test, usuario_tecnico
    ):
        """Test orden vinculada a plan de mantenimiento (Fase 5)"""
        orden = OrdenTrabajo(
            numero_orden="OT-2024-002",
            activo_id=activo_test.id,
            tecnico_id=usuario_tecnico.id,
            plan_mantenimiento_id=plan_mantenimiento_test.id,
            tipo="Preventivo",
            estado="Pendiente",
            descripcion="Orden desde plan",
        )
        db_session.add(orden)
        db_session.commit()

        # Verificar relación con plan
        assert orden.plan_mantenimiento_id == plan_mantenimiento_test.id
        assert orden.plan_mantenimiento.nombre == "Plan Test Mensual"

    def test_relacion_backref_ordenes_generadas(
        self, db_session, plan_mantenimiento_test, activo_test, usuario_tecnico
    ):
        """Test backref ordenes_generadas desde plan"""
        # Crear órdenes desde el plan
        orden1 = OrdenTrabajo(
            numero_orden="OT-AUTO-001",
            activo_id=activo_test.id,
            tecnico_id=usuario_tecnico.id,
            plan_mantenimiento_id=plan_mantenimiento_test.id,
            tipo="Preventivo",
            estado="Pendiente",
        )
        orden2 = OrdenTrabajo(
            numero_orden="OT-AUTO-002",
            activo_id=activo_test.id,
            tecnico_id=usuario_tecnico.id,
            plan_mantenimiento_id=plan_mantenimiento_test.id,
            tipo="Preventivo",
            estado="Completada",
        )
        db_session.add_all([orden1, orden2])
        db_session.commit()

        # Verificar backref
        assert hasattr(plan_mantenimiento_test, "ordenes_generadas")
        assert isinstance(plan_mantenimiento_test.ordenes_generadas, list)
        assert len(plan_mantenimiento_test.ordenes_generadas) == 2

    def test_orden_sin_plan(self, db_session, activo_test, usuario_tecnico):
        """Test orden manual (sin plan de mantenimiento)"""
        orden = OrdenTrabajo(
            numero_orden="OT-MANUAL-001",
            activo_id=activo_test.id,
            tecnico_id=usuario_tecnico.id,
            tipo="Correctivo",
            estado="Pendiente",
            descripcion="Orden manual correctiva",
        )
        db_session.add(orden)
        db_session.commit()

        assert orden.plan_mantenimiento_id is None
        assert orden.plan_mantenimiento is None

    def test_cambiar_estado_orden(self, db_session, orden_trabajo_test):
        """Test cambio de estado de orden"""
        estados = ["Pendiente", "En Progreso", "Completada"]

        for estado in estados:
            orden_trabajo_test.estado = estado
            db_session.commit()
            assert orden_trabajo_test.estado == estado

    def test_relacion_con_activo(self, db_session, orden_trabajo_test, activo_test):
        """Test relación con activo"""
        assert orden_trabajo_test.activo_id == activo_test.id
        assert orden_trabajo_test.activo.codigo == "ACT-001"
        assert orden_trabajo_test.activo.nombre == "Compresor Test"

    def test_relacion_con_tecnico(
        self, db_session, orden_trabajo_test, usuario_tecnico
    ):
        """Test relación con técnico"""
        assert orden_trabajo_test.tecnico_id == usuario_tecnico.id
        assert orden_trabajo_test.tecnico.username == "tecnico_test"
        assert orden_trabajo_test.tecnico.rol == "Técnico"
