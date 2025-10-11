#!/usr/bin/env python3
"""
Configuración de secretos para producción en Google Cloud - España
"""

import os
from google.cloud import secretmanager


def setup_secrets():
    """Configurar secretos en Google Secret Manager para empresa española"""

    print("🔐 Configurando secretos para producción en España...")

    project_id = "mantenimiento-470311"
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{project_id}"

    secrets_to_create = {
        "flask-secret-key": "Clave secreta para Flask sessions y CSRF",
        "db-password": "Password para usuario de base de datos PostgreSQL",
        "redis-password": "Password para Redis (si es necesario)",
        "admin-password": "Password inicial para usuario administrador",
        "gdpr-encryption-key": "Clave para cifrado de datos personales GDPR",
        "audit-api-key": "Clave para API de auditoría GDPR",
    }

    for secret_id, description in secrets_to_create.items():
        try:
            # Verificar si el secreto ya existe
            secret_name = f"{parent}/secrets/{secret_id}"
            try:
                secret = client.get_secret(request={"name": secret_name})
                print(f"✅ Secreto '{secret_id}' ya existe")
                continue
            except Exception:
                pass

            # Crear el secreto con etiquetas para España/GDPR
            secret = client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": {
                        "replication": {
                            "user_managed": {
                                "replicas": [
                                    {
                                        "location": "europe-west1",
                                        "customer_managed_encryption": {},
                                    }
                                ]
                            }
                        },
                        "labels": {
                            "application": "gmao",
                            "environment": "production",
                            "company": "disfood",
                            "country": "spain",
                            "region": "europe-west1",
                            "gdpr": "compliant",
                        },
                    },
                }
            )

            print(f"✅ Secreto '{secret_id}' creado: {secret.name}")

        except Exception as e:
            print(f"❌ Error creando secreto '{secret_id}': {e}")


def get_secret(secret_id, project_id="mantenimiento-470311"):
    """Obtener un secreto de Google Secret Manager"""

    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")

    except Exception as e:
        print(f"❌ Error obteniendo secreto '{secret_id}': {e}")
        return None


def configure_app_secrets():
    """Configurar variables de entorno desde secretos"""

    secrets_map = {
        "SECRET_KEY": "flask-secret-key",
        "DB_PASSWORD": "db-password",
        "REDIS_PASSWORD": "redis-password",
        "ADMIN_INITIAL_PASSWORD": "admin-password",
    }

    for env_var, secret_id in secrets_map.items():
        secret_value = get_secret(secret_id)
        if secret_value:
            os.environ[env_var] = secret_value
            print(f"✅ Variable {env_var} configurada desde Secret Manager")
        else:
            print(f"⚠️ No se pudo obtener secreto para {env_var}")


if __name__ == "__main__":
    setup_secrets()
