"""
Configuración de pytest y fixtures compartidas para tests
"""

import pytest
import sys
from pathlib import Path

# Agregar app al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.factory import create_app
from app.extensions import db
from app.models.usuario import Usuario
from app.models.activo import Activo
from app.models.orden_trabajo import OrdenTrabajo
from app.models.plan_mantenimiento import PlanMantenimiento


@pytest.fixture(scope="session")
def app():
    """Crea la aplicación Flask para testing"""
    app = create_app()

    # Configuración para testing
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
            "FLASK_ENV": "development",  # Cambiado de "testing" a "development" para cron
            "SERVER_URL": "http://localhost:5000",
        }
    )

    # Crear todas las tablas
    with app.app_context():
        db.create_all()

    yield app

    # Limpiar después de los tests
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de prueba para hacer requests"""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Sesión de base de datos limpia para cada test"""
    with app.app_context():
        # Limpiar tablas antes de cada test
        db.session.remove()
        db.drop_all()
        db.create_all()

        yield db.session

        # Limpiar después del test
        db.session.remove()
        db.drop_all()


@pytest.fixture
def usuario_admin(db_session):
    """Usuario administrador de prueba"""
    usuario = Usuario(
        username="admin_test", email="admin@test.com", rol="Administrador"
    )
    usuario.set_password("admin123")
    db_session.add(usuario)
    db_session.commit()
    return usuario


@pytest.fixture
def usuario_tecnico(db_session):
    """Usuario técnico de prueba"""
    usuario = Usuario(username="tecnico_test", email="tecnico@test.com", rol="Técnico")
    usuario.set_password("tecnico123")
    db_session.add(usuario)
    db_session.commit()
    return usuario


@pytest.fixture
def activo_test(db_session):
    """Activo de prueba"""
    activo = Activo(
        codigo="ACT-001",
        nombre="Compresor Test",
        departamento="Producción",
        tipo="Compresor",
        ubicacion="Planta 1",
        estado="Operativo",
        activo=True,
    )
    db_session.add(activo)
    db_session.commit()
    return activo


@pytest.fixture
def plan_mantenimiento_test(db_session, activo_test):
    """Plan de mantenimiento de prueba"""
    from datetime import datetime, timedelta

    plan = PlanMantenimiento(
        codigo_plan="PLAN-TEST-001",
        nombre="Plan Test Mensual",
        activo_id=activo_test.id,
        tipo_frecuencia="mensual",
        frecuencia_dias=30,
        proxima_ejecucion=datetime.now() - timedelta(days=5),  # Vencido
        descripcion="Plan de prueba",
        estado="Activo",
    )
    db_session.add(plan)
    db_session.commit()
    return plan


@pytest.fixture
def orden_trabajo_test(db_session, activo_test, usuario_tecnico):
    """Orden de trabajo de prueba"""
    orden = OrdenTrabajo(
        numero_orden=f"OT-TEST-001",
        activo_id=activo_test.id,
        tipo="Correctivo",
        prioridad="Media",
        estado="Pendiente",
        descripcion="Orden de prueba",
        tecnico_id=usuario_tecnico.id,
    )
    db_session.add(orden)
    db_session.commit()
    return orden
