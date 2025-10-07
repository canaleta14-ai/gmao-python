"""
Configuración de pytest y fixtures compartidas para tests
"""

import pytest
import sys
from pathlib import Path

# Agregar app al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import os
from datetime import datetime
from app.factory import create_app
from app.extensions import db
from app.models.usuario import Usuario
from app.models.activo import Activo
from app.models.orden_trabajo import OrdenTrabajo
from app.models.plan_mantenimiento import PlanMantenimiento


@pytest.fixture(scope="session")
def app():
    """Crea la aplicación Flask para testing"""
    # Forzar configuración de BD antes de inicializar la app
    # Activar explícitamente el modo testing para que create_app configure correctamente
    os.environ["TESTING"] = "true"
    os.environ["DB_TYPE"] = "sqlite"
    os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"

    app = create_app()

    # Configuración para testing
    app.config.update(
        {
            "TESTING": True,
            # (El URI se aplica desde variable de entorno antes de create_app)
            # Permitir acceso desde múltiples hilos si los tests abren varias conexiones
            "SQLALCHEMY_ENGINE_OPTIONS": {"connect_args": {"check_same_thread": False}},
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "WTF_CSRF_ENABLED": False,
            # Clave secreta larga para cumplir requisitos de seguridad en tests
            "SECRET_KEY": "x" * 64,
            "FLASK_ENV": "development",  # Cambiado de "testing" a "development" para cron
            "SERVER_URL": "http://localhost:5000",
            # Desactivar rate limiting en tests para evitar 429 o errores
            "RATELIMIT_ENABLED": False,
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


@pytest.fixture(scope="function")
def authenticated_client(app, client):
    """Cliente con sesión autenticada para pruebas de seguridad."""
    # Crear usuario admin si no existe
    with app.app_context():
        admin = Usuario.query.filter_by(username="admin").first()
        if not admin:
            admin = Usuario(
                username="admin",
                email="admin@example.com",
                nombre="Administrador",
                rol="Administrador",
                activo=True,
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

    # Iniciar sesión usando el endpoint de login JSON sin mantener
    # el contexto del cliente abierto durante toda la prueba.
    resp = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code in [200, 302]
    return client


@pytest.fixture
def db_session(app):
    """Sesión de base de datos limpia para cada test"""
    with app.app_context():
        # Asegurar aislamiento: limpiar y recrear tablas en cada test
        db.session.remove()
        db.drop_all()
        db.create_all()

        yield db.session

        # Limpiar sesión después del test sin borrar tablas
        db.session.rollback()
        db.session.remove()


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


# Fixture alternativo que usa la sesión del app sin limpiar tablas,
# pensado para pruebas que combinan autenticación y creación de Activo.
@pytest.fixture
def activo_test_app(app):
    with app.app_context():
        activo = Activo(
            nombre="Laptop X",
            descripcion="Equipo portátil para desarrollo",
            categoria="Electrónica",
            numero_serie="SN-001",
            estado="activo",
            ubicacion="Oficina",
            responsable="Admin",
            valor=1500.0,
            fecha_adquisicion=datetime(2024, 1, 15),
        )
        db.session.add(activo)
        db.session.commit()
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
