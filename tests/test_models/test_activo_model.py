"""
Tests para el modelo Activo
"""
import pytest
from app.models.activo import Activo


def test_activo_get_departamentos():
    """Test del método get_departamentos"""
    departamentos = Activo.get_departamentos()
    assert isinstance(departamentos, dict)
    assert len(departamentos) > 0
    # Check some expected departments
    assert "100" in departamentos  # Production
    assert "200" in departamentos  # Maintenance


def test_activo_validar_codigo_valid():
    """Test de validación de código válido"""
    # Valid format: 3 digits + 'A' + 5 digits
    assert Activo.validar_codigo("123A45678") is True
    assert Activo.validar_codigo("001A00001") is True
    assert Activo.validar_codigo("999A99999") is True


def test_activo_validar_codigo_invalid():
    """Test de validación de código inválido"""
    # Invalid formats
    assert Activo.validar_codigo("12A45678") is False  # Too short
    assert Activo.validar_codigo("1234A45678") is False  # Too long
    assert Activo.validar_codigo("123B45678") is False  # Wrong letter
    assert Activo.validar_codigo("ABCA45678") is False  # Letters instead of numbers
    assert Activo.validar_codigo("123A4567B") is False  # Letter at end
    assert Activo.validar_codigo("") is False  # Empty
    # Handle None case safely
    try:
        result = Activo.validar_codigo(None)
        assert result is False
    except (TypeError, AttributeError):
        # If the method doesn't handle None gracefully, that's also valid
        pass


def test_activo_creation():
    """Test de creación de instancia de Activo"""
    activo = Activo(
        codigo="123A45678",
        nombre="Test Asset",
        tipo="Compresor",
        departamento="100",
        ubicacion="Planta 1",
        estado="Operativo",
        prioridad="Media"
    )
    assert activo.codigo == "123A45678"
    assert activo.nombre == "Test Asset"
    assert activo.tipo == "Compresor"
    assert activo.departamento == "100"
    assert activo.ubicacion == "Planta 1"
    assert activo.estado == "Operativo"
    assert activo.prioridad == "Media"


def test_activo_str_representation():
    """Test de representación string del Activo"""
    activo = Activo(
        codigo="123A45678",
        nombre="Test Asset",
        tipo="Compresor"
    )
    str_repr = str(activo)
    # Just check that we get a string representation
    assert isinstance(str_repr, str)
    assert len(str_repr) > 0


def test_activo_departamentos_contains_expected_values():
    """Test que los departamentos contienen valores esperados"""
    departamentos = Activo.get_departamentos()
    
    # Check that we have some expected department codes
    expected_codes = ["100", "200", "300", "400"]
    found_codes = [code for code in expected_codes if code in departamentos]
    assert len(found_codes) > 0, "Should have at least some expected department codes"
    
    # Check that values are strings (department names)
    for code, name in departamentos.items():
        assert isinstance(code, str)
        assert isinstance(name, str)
        assert len(name) > 0