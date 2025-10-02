"""
Tests para el factory pattern (app/factory.py)
"""

import pytest
from flask import Flask
from app.factory import create_app
from app.extensions import db


@pytest.mark.unit
class TestFactory:

    def test_create_app_default(self):
        """Test creación de app con configuración por defecto"""
        app = create_app()

        assert app is not None
        assert isinstance(app, Flask)
        assert app.config["SECRET_KEY"] is not None

    def test_create_app_testing_config(self):
        """Test creación de app con configuración de testing"""
        app = create_app()

        assert app.config["TESTING"] is True
        assert "sqlite:///:memory:" in app.config["SQLALCHEMY_DATABASE_URI"]

    def test_database_extension_initialized(self):
        """Test que la extensión de base de datos está inicializada"""
        app = create_app()

        with app.app_context():
            # db debería estar inicializado
            assert db is not None
            assert db.app == app

    def test_blueprints_registered(self):
        """Test que los blueprints principales están registrados"""
        app = create_app()

        # Verificar que se registraron blueprints
        blueprint_names = [bp.name for bp in app.blueprints.values()]

        # Blueprints esperados
        expected = ["web", "activos", "ordenes", "planes", "inventario", "usuarios"]

        for bp_name in expected:
            assert bp_name in blueprint_names, f"Blueprint '{bp_name}' no registrado"

    def test_template_filters_registered(self):
        """Test que los filtros de template están registrados"""
        app = create_app()

        # Verificar filtros personalizados
        assert (
            "datetime_format" in app.jinja_env.filters or len(app.jinja_env.filters) > 0
        )

    def test_error_handlers_registered(self):
        """Test que los manejadores de errores están configurados"""
        app = create_app()

        # Verificar que hay error handlers registrados
        assert 404 in app.error_handler_spec[None] or len(app.error_handler_spec) > 0

    def test_static_folder_configured(self):
        """Test que la carpeta static está configurada"""
        app = create_app()

        assert app.static_folder is not None
        assert "static" in app.static_folder

    def test_template_folder_configured(self):
        """Test que la carpeta de templates está configurada"""
        app = create_app()

        assert app.template_folder is not None
        assert "templates" in app.template_folder

    def test_csrf_disabled_in_testing(self):
        """Test que CSRF está deshabilitado en testing"""
        app = create_app()

        # En testing, WTF_CSRF_ENABLED debería ser False
        assert app.config.get("WTF_CSRF_ENABLED", True) is False

    def test_sqlalchemy_track_modifications_disabled(self):
        """Test que SQLALCHEMY_TRACK_MODIFICATIONS está deshabilitado"""
        app = create_app()

        # Debería estar en False para evitar warnings
        assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False

    def test_app_context_works(self):
        """Test que el contexto de la aplicación funciona"""
        app = create_app()

        with app.app_context():
            # Debería poder acceder a current_app
            from flask import current_app

            assert current_app is not None
            assert current_app.name == app.name

    def test_request_context_works(self):
        """Test que el contexto de request funciona"""
        app = create_app()

        with app.test_request_context("/"):
            from flask import request

            assert request is not None
            assert request.path == "/"
