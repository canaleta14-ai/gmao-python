#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Verificación: Fase 3 - Secret Manager

Verifica que Google Cloud Secret Manager esté correctamente configurado.

Uso:
    python scripts/verify_fase3.py
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Imprime encabezado con formato"""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print("=" * 60)


def print_check(name, passed, details=""):
    """Imprime resultado de verificación"""
    status = "OK" if passed else "FALLO"
    symbol = "✓" if passed else "✗"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"

    print(f"{color}{symbol}{reset} {name}: {status}")
    if details:
        print(f"  → {details}")


def main():
    print_header("VERIFICACIÓN FASE 3: GOOGLE CLOUD SECRET MANAGER")

    checks_passed = 0
    checks_total = 0

    # Directorio raíz del proyecto
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # ========== VERIFICACIÓN 1: google-cloud-secret-manager instalado ==========
    checks_total += 1
    try:
        from google.cloud import secretmanager

        print_check("google-cloud-secret-manager instalado", True, "Módulo disponible")
        checks_passed += 1
    except ImportError:
        print_check(
            "google-cloud-secret-manager instalado",
            False,
            "Ejecutar: pip install google-cloud-secret-manager",
        )

    # ========== VERIFICACIÓN 2: app/utils/secrets.py existe ==========
    checks_total += 1
    secrets_file = project_root / "app" / "utils" / "secrets.py"
    if secrets_file.exists():
        print_check("app/utils/secrets.py existe", True, str(secrets_file))
        checks_passed += 1
    else:
        print_check(
            "app/utils/secrets.py existe", False, "Archivo de utilidades faltante"
        )

    # ========== VERIFICACIÓN 3: Funciones en secrets.py ==========
    checks_total += 1
    if secrets_file.exists():
        content = secrets_file.read_text(encoding="utf-8")
        if "def get_secret(" in content and "def get_secret_or_env(" in content:
            print_check(
                "Funciones get_secret y get_secret_or_env",
                True,
                "Ambas funciones definidas",
            )
            checks_passed += 1
        else:
            print_check(
                "Funciones get_secret y get_secret_or_env",
                False,
                "Funciones faltantes o mal definidas",
            )
    else:
        print_check(
            "Funciones get_secret y get_secret_or_env",
            False,
            "Archivo secrets.py no existe",
        )

    # ========== VERIFICACIÓN 4: factory.py usa get_secret_or_env ==========
    checks_total += 1
    factory_file = project_root / "app" / "factory.py"
    if factory_file.exists():
        content = factory_file.read_text(encoding="utf-8")
        if "from app.utils.secrets import get_secret_or_env" in content:
            print_check(
                "factory.py importa get_secret_or_env", True, "Importación correcta"
            )
            checks_passed += 1
        else:
            print_check(
                "factory.py importa get_secret_or_env", False, "Falta importación"
            )
    else:
        print_check(
            "factory.py importa get_secret_or_env",
            False,
            "Archivo factory.py no encontrado",
        )

    # ========== VERIFICACIÓN 5: SECRET_KEY usa Secret Manager ==========
    checks_total += 1
    if factory_file.exists():
        content = factory_file.read_text(encoding="utf-8")
        if "get_secret_or_env" in content and "gmao-secret-key" in content:
            print_check("SECRET_KEY usa Secret Manager", True, "Configuración correcta")
            checks_passed += 1
        else:
            print_check(
                "SECRET_KEY usa Secret Manager", False, "No configurado correctamente"
            )
    else:
        print_check("SECRET_KEY usa Secret Manager", False, "factory.py no encontrado")

    # ========== VERIFICACIÓN 6: DB_PASSWORD usa Secret Manager ==========
    checks_total += 1
    if factory_file.exists():
        content = factory_file.read_text(encoding="utf-8")
        if "gmao-db-password" in content:
            print_check(
                "DB_PASSWORD usa Secret Manager", True, "Configuración correcta"
            )
            checks_passed += 1
        else:
            print_check(
                "DB_PASSWORD usa Secret Manager", False, "No configurado correctamente"
            )
    else:
        print_check("DB_PASSWORD usa Secret Manager", False, "factory.py no encontrado")

    # ========== VERIFICACIÓN 7: MAIL_PASSWORD usa Secret Manager ==========
    checks_total += 1
    if factory_file.exists():
        content = factory_file.read_text(encoding="utf-8")
        if "gmao-mail-password" in content:
            print_check(
                "MAIL_PASSWORD usa Secret Manager", True, "Configuración correcta"
            )
            checks_passed += 1
        else:
            print_check(
                "MAIL_PASSWORD usa Secret Manager",
                False,
                "No configurado correctamente",
            )
    else:
        print_check(
            "MAIL_PASSWORD usa Secret Manager", False, "factory.py no encontrado"
        )

    # ========== VERIFICACIÓN 8: .env.example actualizado ==========
    checks_total += 1
    env_example = project_root / ".env.example"
    if env_example.exists():
        content = env_example.read_text(encoding="utf-8")
        if "GOOGLE_CLOUD_PROJECT" in content and "Secret Manager" in content:
            print_check(
                ".env.example actualizado",
                True,
                "Documentación de Secret Manager presente",
            )
            checks_passed += 1
        else:
            print_check(
                ".env.example actualizado",
                False,
                "Falta documentación de Secret Manager",
            )
    else:
        print_check(
            ".env.example actualizado", False, "Archivo .env.example no encontrado"
        )

    # ========== VERIFICACIÓN 9: requirements.txt actualizado ==========
    checks_total += 1
    req_file = project_root / "requirements.txt"
    if req_file.exists():
        content = req_file.read_text(encoding="utf-8")
        if "google-cloud-secret-manager" in content:
            print_check(
                "google-cloud-secret-manager en requirements.txt",
                True,
                "Dependencia registrada",
            )
            checks_passed += 1
        else:
            print_check(
                "google-cloud-secret-manager en requirements.txt",
                False,
                "Ejecutar: pip freeze > requirements.txt",
            )
    else:
        print_check(
            "google-cloud-secret-manager en requirements.txt",
            False,
            "requirements.txt no encontrado",
        )

    # ========== VERIFICACIÓN 10: Autenticación GCP (opcional en dev) ==========
    checks_total += 1
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    gcloud_config = Path.home() / ".config" / "gcloud"
    if creds_path or gcloud_config.exists():
        print_check(
            "Autenticación GCP configurada",
            True,
            "gcloud configurado o GOOGLE_APPLICATION_CREDENTIALS presente",
        )
        checks_passed += 1
    else:
        print_check(
            "Autenticación GCP configurada (opcional)",
            True,
            "No configurado (OK en desarrollo sin GCP)",
        )
        checks_passed += 1  # No es obligatorio en desarrollo

    # ========== VERIFICACIÓN 11: Test de importación ==========
    checks_total += 1
    try:
        from app.utils.secrets import get_secret_or_env, REQUIRED_SECRETS

        print_check(
            "Importación de módulo secrets",
            True,
            f"{len(REQUIRED_SECRETS)} secrets definidos",
        )
        checks_passed += 1
    except Exception as e:
        print_check("Importación de módulo secrets", False, f"Error: {e}")

    # ========== VERIFICACIÓN 12: No hay secrets hardcodeados ==========
    checks_total += 1
    if factory_file.exists():
        content = factory_file.read_text(encoding="utf-8")
        # Buscar patrones sospechosos (no exhaustivo)
        suspicious = [
            'SECRET_KEY = "clave_secreta_fija_para_sesiones',
            'DB_PASSWORD = "',
            'MAIL_PASSWORD = "',
        ]
        has_hardcoded = any(pattern in content for pattern in suspicious)
        if not has_hardcoded:
            print_check(
                "Sin secrets hardcodeados",
                True,
                "No se encontraron credenciales en código",
            )
            checks_passed += 1
        else:
            print_check(
                "Sin secrets hardcodeados",
                False,
                "Se encontraron posibles credenciales hardcodeadas",
            )
    else:
        print_check(
            "Sin secrets hardcodeados", False, "No se pudo verificar factory.py"
        )

    # ========== RESUMEN FINAL ==========
    print_header("RESUMEN DE VERIFICACIÓN")

    percentage = (checks_passed / checks_total) * 100
    print(
        f"\nVerificaciones pasadas: {checks_passed}/{checks_total} ({percentage:.1f}%)"
    )

    if checks_passed == checks_total:
        print("\n✅ FASE 3 COMPLETADA EXITOSAMENTE")
        print("Secret Manager está correctamente configurado.")
        print("\nPróximos pasos:")
        print("  1. Crear secrets en GCP (si aún no existen)")
        print("  2. Configurar autenticación: gcloud auth application-default login")
        print("  3. Probar aplicación: python run.py")
        return 0
    elif checks_passed >= checks_total * 0.8:
        print("\n⚠️  FASE 3 CASI COMPLETA")
        print("Algunas verificaciones fallaron, pero lo principal está configurado.")
        print("Revisa los puntos marcados como FALLO.")
        return 1
    else:
        print("\n❌ FASE 3 INCOMPLETA")
        print("Varias verificaciones fallaron. Completa los pasos faltantes.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
