"""
Utilidades para Google Cloud Secret Manager

Proporciona funciones para acceder a secretos almacenados en GCP de forma segura.
Incluye fallback a variables de entorno para desarrollo local.
"""

import os
import logging
from typing import Optional

# Lazy import para evitar errores si google-cloud no está instalado en desarrollo
try:
    from google.cloud import secretmanager

    SECRETMANAGER_AVAILABLE = True
except ImportError:
    SECRETMANAGER_AVAILABLE = False

logger = logging.getLogger(__name__)


def get_secret(
    secret_id: str, project_id: Optional[str] = None, version: str = "latest"
) -> Optional[str]:
    """
    Obtiene un secreto desde Google Cloud Secret Manager.

    Args:
        secret_id: ID del secreto en GCP (e.g., 'gmao-secret-key')
        project_id: ID del proyecto GCP (opcional, se obtiene de env)
        version: Versión del secreto a obtener (default: 'latest')

    Returns:
        Valor del secreto como string, o None si falla

    Example:
        >>> secret_key = get_secret('gmao-secret-key')
        >>> db_password = get_secret('gmao-db-password')

    Note:
        Requiere autenticación GCP configurada (gcloud auth login)
        y permisos 'roles/secretmanager.secretAccessor'
    """
    if not SECRETMANAGER_AVAILABLE:
        logger.warning(
            f"google-cloud-secret-manager no disponible, "
            f"no se puede acceder a '{secret_id}'"
        )
        return None

    try:
        # Obtener project_id desde env si no se proporciona
        if project_id is None:
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "gmao-sistema")

        # Crear cliente de Secret Manager
        client = secretmanager.SecretManagerServiceClient()

        # Construir nombre completo del secreto
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"

        # Acceder al secreto
        response = client.access_secret_version(request={"name": name})

        # Decodificar payload
        secret_value = response.payload.data.decode("UTF-8")

        logger.info(f"Secret '{secret_id}' obtenido desde Secret Manager")
        return secret_value

    except Exception as e:
        logger.error(f"Error al obtener secret '{secret_id}' de Secret Manager: {e}")
        return None


def get_secret_or_env(secret_id: str, env_var: str, default: str = "") -> str:
    """
    Obtiene secreto de Secret Manager en producción o variable de entorno en desarrollo.

    Esta función implementa el patrón de fallback:
    1. Si está en GCP (producción): Intenta Secret Manager
    2. Si falla o está en local: Usa variable de entorno
    3. Si falla todo: Usa valor por defecto

    Args:
        secret_id: ID del secreto en GCP (e.g., 'gmao-secret-key')
        env_var: Nombre de variable de entorno alternativa (e.g., 'SECRET_KEY')
        default: Valor por defecto si ambos fallan (default: "")

    Returns:
        Valor del secreto/env/default

    Example:
        >>> # En producción: obtiene de Secret Manager
        >>> # En desarrollo: obtiene de .env
        >>> secret_key = get_secret_or_env(
        ...     secret_id='gmao-secret-key',
        ...     env_var='SECRET_KEY',
        ...     default='dev-insecure-key'
        ... )

    Note:
        Detecta automáticamente el entorno basándose en:
        - GAE_ENV: Google App Engine
        - K_SERVICE: Google Cloud Run
        - GOOGLE_CLOUD_PROJECT: Proyecto GCP configurado
    """
    # Detectar si estamos en entorno GCP
    is_gcp = (
        os.getenv("GAE_ENV", "").startswith("standard")  # App Engine
        or os.getenv("K_SERVICE") is not None  # Cloud Run
        or os.getenv("GOOGLE_CLOUD_PROJECT") is not None  # GCP configurado
    )

    # En GCP, intentar Secret Manager primero
    if is_gcp and SECRETMANAGER_AVAILABLE:
        logger.debug(
            f"Entorno GCP detectado, intentando Secret Manager para '{secret_id}'"
        )
        secret_value = get_secret(secret_id)
        if secret_value:
            return secret_value
        else:
            logger.warning(
                f"Secret '{secret_id}' no disponible en Secret Manager, "
                f"usando variable de entorno '{env_var}'"
            )

    # Fallback: Variable de entorno (desarrollo o si Secret Manager falla)
    env_value = os.getenv(env_var, default)

    if env_value == default and default:
        logger.warning(
            f"Usando valor por defecto para '{env_var}' "
            f"(ni Secret Manager ni .env disponibles)"
        )
    elif env_value != default:
        logger.debug(f"Usando variable de entorno '{env_var}' para configuración")

    return env_value


def validate_secrets(required_secrets: list[str]) -> dict[str, bool]:
    """
    Valida que los secretos requeridos estén disponibles en Secret Manager.

    Útil para verificar configuración en startup de la aplicación.

    Args:
        required_secrets: Lista de IDs de secretos requeridos

    Returns:
        Dict con secret_id como key y bool (disponible/no disponible) como value

    Example:
        >>> secrets_status = validate_secrets([
        ...     'gmao-secret-key',
        ...     'gmao-db-password',
        ...     'gmao-mail-password'
        ... ])
        >>> if not all(secrets_status.values()):
        ...     print("❌ Algunos secretos no están disponibles")
    """
    results = {}

    for secret_id in required_secrets:
        secret_value = get_secret(secret_id)
        results[secret_id] = secret_value is not None

    return results


# Constantes de secrets comunes del sistema
SECRET_FLASK_KEY = "gmao-secret-key"
SECRET_DB_PASSWORD = "gmao-db-password"
SECRET_MAIL_PASSWORD = "gmao-mail-password"

# Lista de secretos requeridos en producción
REQUIRED_SECRETS = [
    SECRET_FLASK_KEY,
    SECRET_DB_PASSWORD,
    SECRET_MAIL_PASSWORD,
]
