"""
Tests unitarios para el modelo Activo
"""

import pytest
from datetime import datetime
from app.models.activo import Activo


@pytest.mark.unit
class TestActivoModel:

    def test_crear_activo_basico(self, db_session):
        """Test creación básica de activo"""
        activo = Activo(
            codigo="ACT-TEST-001",
            nombre="Bomba Centrífuga",
            departamento="Producción",
            tipo="Bomba",
            ubicacion="Planta 2",
            estado="Operativo",
            activo=True,
        )
        db_session.add(activo)
        db_session.commit()

        assert activo.id is not None
        assert activo.codigo == "ACT-TEST-001"
        assert activo.nombre == "Bomba Centrífuga"
        assert activo.estado == "Operativo"
        assert activo.activo is True

    def test_activo_con_todos_los_campos(self, db_session):
        """Test activo con todos los campos opcionales"""
        activo = Activo(
            codigo="ACT-FULL-001",
            nombre="Compresor Industrial",
            departamento="140",
            tipo="Compresor",
            ubicacion="Almacén Central",
            estado="En Mantenimiento",
            fabricante="Siemens",
            modelo="X-2000",
            numero_serie="SN123456789",
            fecha_adquisicion=datetime(2024, 1, 15),
            prioridad="Alta",
            activo=True,
        )
        db_session.add(activo)
        db_session.commit()

        assert activo.fabricante == "Siemens"
        assert activo.modelo == "X-2000"
        assert activo.numero_serie == "SN123456789"
        assert activo.prioridad == "Alta"

    def test_activo_activo_vs_inactivo(self, db_session):
        """Test diferencia entre activo activo e inactivo"""
        activo_operativo = Activo(
            codigo="ACT-OP-001",
            nombre="Activo Operativo",
            departamento="Producción",
            tipo="Máquina",
            ubicacion="Planta 1",
            estado="Operativo",
            activo=True,
        )

        activo_dado_baja = Activo(
            codigo="ACT-BAJA-001",
            nombre="Activo Dado de Baja",
            departamento="Producción",
            tipo="Máquina",
            ubicacion="Almacén",
            estado="Fuera de Servicio",
            activo=False,
        )

        db_session.add_all([activo_operativo, activo_dado_baja])
        db_session.commit()

        # Verificar que solo activos activos se listan normalmente
        activos_activos = Activo.query.filter_by(activo=True).all()
        assert len(activos_activos) == 1
        assert activos_activos[0].codigo == "ACT-OP-001"

    def test_relacion_con_ordenes_trabajo(
        self, db_session, activo_test, orden_trabajo_test
    ):
        """Test relación backref con órdenes de trabajo"""
        # activo_test ya tiene una orden_trabajo_test asociada
        ordenes = activo_test.ordenes

        assert ordenes is not None
        assert len(ordenes) >= 1
        assert orden_trabajo_test in ordenes

    def test_codigo_unico(self, db_session):
        """Test que el código del activo debe ser único"""
        activo1 = Activo(
            codigo="ACT-UNIQUE-001",
            nombre="Activo 1",
            departamento="Producción",
            tipo="Máquina",
            ubicacion="Planta 1",
            estado="Operativo",
            activo=True,
        )
        db_session.add(activo1)
        db_session.commit()

        # Intentar crear otro con el mismo código debería fallar
        activo2 = Activo(
            codigo="ACT-UNIQUE-001",  # Mismo código
            nombre="Activo 2",
            departamento="Producción",
            tipo="Máquina",
            ubicacion="Planta 2",
            estado="Operativo",
            activo=True,
        )
        db_session.add(activo2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_estados_validos(self, db_session):
        """Test diferentes estados válidos de activo"""
        estados = [
            "Operativo",
            "En Mantenimiento",
            "Fuera de Servicio",
            "En Reparación",
        ]

        for i, estado in enumerate(estados):
            activo = Activo(
                codigo=f"ACT-ESTADO-{i:03d}",
                nombre=f"Activo Estado {estado}",
                departamento="Producción",
                tipo="Máquina",
                ubicacion="Planta 1",
                estado=estado,
                activo=True,
            )
            db_session.add(activo)

        db_session.commit()

        # Verificar que todos se crearon
        activos_creados = Activo.query.filter(Activo.codigo.like("ACT-ESTADO-%")).all()
        assert len(activos_creados) == len(estados)

    def test_prioridades_validas(self, db_session):
        """Test diferentes niveles de prioridad"""
        prioridades = ["Baja", "Media", "Alta", "Crítica"]

        for i, prioridad in enumerate(prioridades):
            activo = Activo(
                codigo=f"ACT-PRIOR-{i:03d}",
                nombre=f"Activo Prioridad {prioridad}",
                departamento="Producción",
                tipo="Máquina",
                ubicacion="Planta 1",
                estado="Operativo",
                prioridad=prioridad,
                activo=True,
            )
            db_session.add(activo)

        db_session.commit()

        # Verificar activos críticos
        criticos = Activo.query.filter_by(prioridad="Crítica").all()
        assert len(criticos) == 1
        assert criticos[0].prioridad == "Crítica"
