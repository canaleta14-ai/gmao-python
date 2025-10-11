"""
Utilidades para gestores de secretos (GCP/AWS/Azure)

Proporciona funciones para acceder a secretos almacenados en:
- Google Cloud Secret Manager
- AWS Secrets Manager
- Azure Key Vault

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

# Lazy import AWS (boto3)
try:
    import boto3

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

# Lazy import Azure Key Vault
try:
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient

    AZURE_KV_AVAILABLE = True
except ImportError:
    AZURE_KV_AVAILABLE = False

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


def get_secret_aws(secret_id: str, region: Optional[str] = None) -> Optional[str]:
    """Obtiene un secreto desde AWS Secrets Manager.

    Args:
        secret_id: Nombre/ARN del secreto en AWS
        region: Región AWS (fallback a env `AWS_REGION`)

    Returns:
        Valor del secreto como string, o None si falla
    """
    if not BOTO3_AVAILABLE:
        logger.warning("boto3 no disponible, no se puede acceder a AWS Secrets Manager")
        return None

    try:
        if region is None:
            region = os.getenv("AWS_REGION", "us-east-1")

        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_id)

        if "SecretString" in response:
            return response["SecretString"]
        else:
            # Binario -> texto
            import base64

            return base64.b64decode(response["SecretBinary"]).decode("utf-8")
    except Exception as e:
        logger.error(
            f"Error al obtener secret '{secret_id}' de AWS Secrets Manager: {e}"
        )
        return None


def get_secret_azure(secret_id: str, vault_name: Optional[str] = None) -> Optional[str]:
    """Obtiene un secreto desde Azure Key Vault.

    Args:
        secret_id: Nombre del secreto en el Vault
        vault_name: Nombre del Key Vault (fallback a env `AZURE_KEYVAULT_NAME`)

    Returns:
        Valor del secreto como string, o None si falla
    """
    if not AZURE_KV_AVAILABLE:
        logger.warning(
            "azure-keyvault-secrets o azure-identity no disponibles, no se puede acceder a Azure Key Vault"
        )
        return None

    try:
        if vault_name is None:
            vault_name = os.getenv("AZURE_KEYVAULT_NAME")
        if not vault_name:
            logger.error("AZURE_KEYVAULT_NAME no configurado")
            return None

        credential = DefaultAzureCredential()
        vault_url = f"https://{vault_name}.vault.azure.net"
        client = SecretClient(vault_url=vault_url, credential=credential)
        secret = client.get_secret(secret_id)
        return secret.value
    except Exception as e:
        logger.error(f"Error al obtener secret '{secret_id}' de Azure Key Vault: {e}")
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
    # Selección de proveedor
    provider = os.getenv("SECRETS_PROVIDER", "auto").lower()

    def _try_gcp():
        if SECRETMANAGER_AVAILABLE:
            logger.debug(f"Intentando Secret Manager (GCP) para '{secret_id}'")
            value = get_secret(secret_id)
            if value:
                return value
        return None

    def _try_aws():
        logger.debug(f"Intentando Secrets Manager (AWS) para '{secret_id}'")
        return get_secret_aws(secret_id)

    def _try_azure():
        logger.debug(f"Intentando Key Vault (Azure) para '{secret_id}'")
        return get_secret_azure(secret_id)

    value = None

    if provider == "gcp":
        value = _try_gcp()
    elif provider == "aws":
        value = _try_aws()
    elif provider == "azure":
        value = _try_azure()
    else:
        # auto: detectar entorno
        # Detectar automáticamente si estamos en GCP
        is_gcp = (
            os.getenv("GAE_ENV", "").startswith("standard")
            or os.getenv("K_SERVICE") is not None
            or os.getenv("GOOGLE_CLOUD_PROJECT") is not None
        )
        if is_gcp:
            value = _try_gcp()
        # Si no GCP, probar Azure si hay configuración
        if value is None and os.getenv("AZURE_KEYVAULT_NAME"):
            value = _try_azure()
        # Si no Azure, probar AWS si hay configuración
        if value is None and (
            os.getenv("AWS_REGION") or os.getenv("AWS_EXECUTION_ENV")
        ):
            value = _try_aws()

    if value:
        return value

    # Fallback: Variable de entorno (desarrollo o si proveedores fallan)
    env_value = os.getenv(env_var, default)

    if env_value == default and default:
        logger.warning(
            f"Usando valor por defecto para '{env_var}' "
            f"(ningún proveedor de secretos ni .env disponibles)"
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
