#!/usr/bin/env python3
"""
Módulo de cumplimiento GDPR para GMAO Disfood España
"""

import os
import logging
from datetime import datetime, timedelta
from functools import wraps


class GDPRCompliance:
    """Clase para gestionar el cumplimiento GDPR"""

    def __init__(self):
        self.retention_years = int(os.environ.get("DATA_RETENTION_YEARS", "7"))
        self.logger = logging.getLogger("gdpr")

    def log_data_access(self, user_id, data_type, action):
        """Registrar acceso a datos personales"""
        self.logger.info(
            f"GDPR Access - User: {user_id}, Data: {data_type}, Action: {action}"
        )

    def check_retention_period(self, created_date):
        """Verificar si los datos han superado el período de retención"""
        if not created_date:
            return False

        retention_limit = datetime.now() - timedelta(days=self.retention_years * 365)
        return created_date < retention_limit

    def anonymize_data(self, data_dict):
        """Anonimizar datos personales"""
        sensitive_fields = ["email", "telefono", "direccion", "nombre_completo"]

        anonymized = data_dict.copy()
        for field in sensitive_fields:
            if field in anonymized:
                anonymized[field] = f"[ANONIMIZADO_{field.upper()}]"

        return anonymized

    def export_user_data(self, user_id):
        """Exportar todos los datos de un usuario (derecho de portabilidad)"""
        # Esta función debe implementarse según la estructura de la base de datos
        data_export = {
            "user_id": user_id,
            "export_date": datetime.now().isoformat(),
            "data": {},
        }

        # TODO: Implementar exportación de todas las tablas relacionadas
        return data_export

    def delete_user_data(self, user_id):
        """Eliminar todos los datos de un usuario (derecho al olvido)"""
        # Esta función debe implementarse según la estructura de la base de datos
        self.logger.info(f"GDPR Deletion - User: {user_id}")

        # TODO: Implementar eliminación en cascada de todas las tablas
        return True


def gdpr_audit(data_type):
    """Decorador para auditar accesos a datos personales"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Obtener información de usuario desde el contexto de Flask
            try:
                from flask import g

                user_id = getattr(g, "current_user_id", "anonymous")
            except:
                user_id = "system"

            # Registrar el acceso
            gdpr = GDPRCompliance()
            gdpr.log_data_access(user_id, data_type, func.__name__)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def check_gdpr_compliance():
    """Verificar configuración GDPR"""
    checks = {
        "GDPR_COMPLIANCE": os.environ.get("GDPR_COMPLIANCE") == "true",
        "REGION_EU": os.environ.get("GCLOUD_REGION", "").startswith("europe"),
        "DATA_RETENTION": os.environ.get("DATA_RETENTION_YEARS") is not None,
        "TIMEZONE_EU": os.environ.get("TIMEZONE", "").startswith("Europe/"),
    }

    all_compliant = all(checks.values())

    return {
        "compliant": all_compliant,
        "checks": checks,
        "region": os.environ.get("GCLOUD_REGION"),
        "timezone": os.environ.get("TIMEZONE"),
        "retention_years": os.environ.get("DATA_RETENTION_YEARS"),
    }


def generate_privacy_report():
    """Generar reporte de privacidad para auditorías"""
    compliance = check_gdpr_compliance()

    report = {
        "generated_at": datetime.now().isoformat(),
        "compliance_status": compliance,
        "data_locations": {
            "database": f"Cloud SQL - {os.environ.get('GCLOUD_REGION')}",
            "storage": f"Cloud Storage - {os.environ.get('GCLOUD_REGION')}",
            "backups": f"Cloud SQL Backups - {os.environ.get('GCLOUD_REGION')}",
        },
        "retention_policy": {
            "years": os.environ.get("DATA_RETENTION_YEARS", "7"),
            "description": "Documentos de mantenimiento según normativa española",
        },
        "security_measures": {
            "encryption_transit": "HTTPS/TLS",
            "encryption_rest": "Google Cloud KMS",
            "access_control": "Role-based authentication",
            "audit_logging": "Google Cloud Logging",
        },
    }

    return report


# Configuración de cookies GDPR
GDPR_COOKIE_CONFIG = {
    "SESSION_COOKIE_SECURE": True,
    "SESSION_COOKIE_HTTPONLY": True,
    "SESSION_COOKIE_SAMESITE": "Lax",
    "REMEMBER_COOKIE_SECURE": True,
    "REMEMBER_COOKIE_HTTPONLY": True,
    "PERMANENT_SESSION_LIFETIME": timedelta(hours=8),  # Sesión máxima 8 horas
}

# Texto para banner de cookies (España)
COOKIE_BANNER_TEXT_ES = """
Esta web utiliza cookies técnicas necesarias para su funcionamiento.
Al continuar navegando, acepta su uso según nuestra política de cookies.
"""

# Texto para política de privacidad (España)
PRIVACY_POLICY_TEXT_ES = """
## Política de Privacidad - GMAO Disfood

### 1. Responsable del tratamiento
DISFOOD S.L.
CIF: XXXXXXXXX
Dirección: [Dirección de la empresa]
Email: privacidad@disfood.es

### 2. Datos que tratamos
- Datos de usuarios: nombre, email, contraseña
- Datos de mantenimiento: equipos, órdenes, documentos
- Logs de acceso y auditoría

### 3. Finalidad del tratamiento
- Gestión de mantenimiento preventivo y correctivo
- Control de acceso y seguridad
- Cumplimiento de obligaciones legales

### 4. Base legal
- Ejecución de contrato
- Cumplimiento de obligación legal
- Interés legítimo

### 5. Conservación
Los datos se conservan durante 7 años según la normativa española.

### 6. Derechos del interesado
- Acceso, rectificación, supresión
- Portabilidad de datos
- Oposición y limitación del tratamiento

### 7. Transferencias internacionales
Los datos se almacenan en servidores de Google Cloud en la región europea.

### 8. Contacto DPO
Email: dpo@disfood.es
"""


if __name__ == "__main__":
    # Test de configuración GDPR
    compliance = check_gdpr_compliance()
    print("🔒 Estado de cumplimiento GDPR:")
    print(f"✅ Compliant: {compliance['compliant']}")
    print(f"🌍 Región: {compliance['region']}")
    print(f"🕐 Zona horaria: {compliance['timezone']}")
    print(f"📅 Retención: {compliance['retention_years']} años")

    for check, status in compliance["checks"].items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check}: {status}")
