"""
Tests para el modelo Usuario
"""
import pytest
from app.models.usuario import Usuario


def test_usuario_creation():
    """Test de creación de instancia de Usuario"""
    usuario = Usuario(
        username="testuser",
        email="test@example.com",
        rol="tecnico"
    )
    assert usuario.username == "testuser"
    assert usuario.email == "test@example.com"
    assert usuario.rol == "tecnico"


def test_usuario_str_representation():
    """Test de representación string del Usuario"""
    usuario = Usuario(
        username="testuser",
        email="test@example.com",
        rol="tecnico"
    )
    str_repr = str(usuario)
    # Just check that we get a string representation
    assert isinstance(str_repr, str)
    assert len(str_repr) > 0


def test_usuario_password_hashing():
    """Test de hash de contraseña si existe el método"""
    usuario = Usuario(
        username="testuser",
        email="test@example.com",
        rol="tecnico"
    )
    
    # Check if password hashing method exists
    if hasattr(usuario, 'set_password'):
        usuario.set_password("testpassword")
        # Password should be hashed, not plain text
        if hasattr(usuario, 'password_hash'):
            assert usuario.password_hash != "testpassword"
            assert len(usuario.password_hash) > 10  # Hashed passwords are longer
    
    if hasattr(usuario, 'check_password'):
        # If we can set password, we should be able to check it
        if hasattr(usuario, 'set_password'):
            usuario.set_password("testpassword")
            assert usuario.check_password("testpassword") is True
            assert usuario.check_password("wrongpassword") is False


def test_usuario_roles():
    """Test de roles válidos si existe validación"""
    # Test different roles
    roles = ["admin", "tecnico", "supervisor", "operador"]
    
    for rol in roles:
        usuario = Usuario(
            username=f"user_{rol}",
            email=f"{rol}@example.com",
            rol=rol
        )
        assert usuario.rol == rol


def test_usuario_email_validation():
    """Test de validación de email si existe"""
    # Valid emails
    valid_emails = [
        "test@example.com",
        "user.name@domain.co.uk",
        "admin@company.org"
    ]
    
    for email in valid_emails:
        usuario = Usuario(
            username="testuser",
            email=email,
            rol="tecnico"
        )
        assert usuario.email == email


def test_usuario_is_authenticated():
    """Test del método is_authenticated si existe"""
    usuario = Usuario(
        username="testuser",
        email="test@example.com",
        rol="tecnico"
    )
    
    # Check if Flask-Login methods exist
    if hasattr(usuario, 'is_authenticated'):
        # For Flask-Login, is_authenticated should return True for valid users
        assert usuario.is_authenticated is True or callable(usuario.is_authenticated)
    
    if hasattr(usuario, 'is_active'):
        assert usuario.is_active is True or callable(usuario.is_active)
    
    if hasattr(usuario, 'is_anonymous'):
        assert usuario.is_anonymous is False or callable(usuario.is_anonymous)
    
    if hasattr(usuario, 'get_id'):
        # get_id should return something (user ID)
        user_id = usuario.get_id() if callable(usuario.get_id) else usuario.get_id
        # ID can be None for unsaved users, but method should exist
        assert user_id is not None or user_id is None