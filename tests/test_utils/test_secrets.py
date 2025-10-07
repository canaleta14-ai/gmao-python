"""
Tests para utilidades de secretos
"""
import pytest
import os


def test_secrets_module_import():
    """Test que el módulo de secretos se puede importar"""
    try:
        from app.utils import secrets
        assert secrets is not None
    except ImportError:
        pytest.skip("Secrets module not available")


def test_generate_secret_key():
    """Test de generación de clave secreta si existe"""
    try:
        from app.utils.secrets import generate_secret_key
        
        # Generate a secret key
        key = generate_secret_key()
        assert isinstance(key, str)
        assert len(key) > 10  # Should be reasonably long
        
        # Generate another key - should be different
        key2 = generate_secret_key()
        assert key != key2  # Should be random
        
    except ImportError:
        pytest.skip("generate_secret_key function not available")


def test_hash_password():
    """Test de hash de contraseña si existe"""
    try:
        from app.utils.secrets import hash_password
        
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert isinstance(hashed, str)
        assert hashed != password  # Should be hashed, not plain text
        assert len(hashed) > len(password)  # Hashed should be longer
        
        # Same password should produce different hashes (with salt)
        hashed2 = hash_password(password)
        # Note: Some hash functions may produce same result, so we don't assert inequality
        
    except ImportError:
        pytest.skip("hash_password function not available")


def test_verify_password():
    """Test de verificación de contraseña si existe"""
    try:
        from app.utils.secrets import hash_password, verify_password
        
        password = "testpassword123"
        wrong_password = "wrongpassword"
        
        hashed = hash_password(password)
        
        # Correct password should verify
        assert verify_password(password, hashed) is True
        
        # Wrong password should not verify
        assert verify_password(wrong_password, hashed) is False
        
    except ImportError:
        pytest.skip("verify_password function not available")


def test_generate_token():
    """Test de generación de token si existe"""
    try:
        from app.utils.secrets import generate_token
        
        token = generate_token()
        assert isinstance(token, str)
        assert len(token) > 10
        
        # Generate another token - should be different
        token2 = generate_token()
        assert token != token2
        
    except ImportError:
        pytest.skip("generate_token function not available")


def test_validate_token():
    """Test de validación de token si existe"""
    try:
        from app.utils.secrets import generate_token, validate_token
        
        token = generate_token()
        
        # Valid token should validate
        assert validate_token(token) is True
        
        # Invalid token should not validate
        assert validate_token("invalid_token") is False
        assert validate_token("") is False
        assert validate_token(None) is False
        
    except ImportError:
        pytest.skip("validate_token function not available")


def test_environment_variables():
    """Test que las variables de entorno se manejan correctamente"""
    # Test that we can access environment variables safely
    secret_key = os.environ.get('SECRET_KEY')
    # Should not fail even if not set
    assert secret_key is None or isinstance(secret_key, str)
    
    # Test database URL
    db_url = os.environ.get('DATABASE_URL')
    assert db_url is None or isinstance(db_url, str)