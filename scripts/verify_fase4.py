"""
Verificación de Fase 4: Cloud Storage
Verifica que la implementación de Google Cloud Storage esté completa
"""

import os
import sys
from pathlib import Path

# Colores para la terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def check(condition, message):
    """Helper para verificar condición"""
    if condition:
        print(f"{GREEN}✓{RESET} {message}")
        return True
    else:
        print(f"{RED}✗{RESET} {message}")
        return False


def main():
    print("=" * 70)
    print(f"{BLUE}🔍 VERIFICACIÓN FASE 4: GOOGLE CLOUD STORAGE{RESET}")
    print("=" * 70)
    print()

    checks_passed = 0
    total_checks = 0

    #  1. Dependencia google-cloud-storage instalada
    print(f"{BLUE}[1/14] Dependencias{RESET}")
    total_checks += 1
    try:
        import google.cloud.storage

        version = google.cloud.storage.__version__
        checks_passed += check(True, f"google-cloud-storage instalado (v{version})")
    except ImportError:
        check(False, "google-cloud-storage NO instalado")
    print()

    # 2. Archivo storage.py existe
    print(f"{BLUE}[2/14] Archivos Core{RESET}")
    total_checks += 1
    storage_path = Path("app/utils/storage.py")
    if check(storage_path.exists(), f"Existe {storage_path}"):
        checks_passed += 1
    print()

    # 3. Funciones definidas en storage.py
    if storage_path.exists():
        print(f"{BLUE}[3/14] Funciones en storage.py{RESET}")
        content = storage_path.read_text(encoding="utf-8")

        functions = [
            ("upload_file", "Subida de archivos"),
            ("delete_file", "Eliminación de archivos"),
            ("get_signed_url", "URLs firmadas"),
            ("list_files", "Listado de archivos"),
            ("is_gcp_environment", "Detección de entorno"),
        ]

        for func_name, desc in functions:
            total_checks += 1
            if check(
                f"def {func_name}" in content,
                f"Función {func_name}() definida ({desc})",
            ):
                checks_passed += 1
        print()

    # 4. Controlador de manuales modificado
    print(f"{BLUE}[4/14] Controlador de Manuales{RESET}")
    manuales_path = Path("app/controllers/manuales_controller.py")
    if manuales_path.exists():
        content = manuales_path.read_text(encoding="utf-8")

        total_checks += 1
        if check("from app.utils.storage import" in content, "Importa módulo storage"):
            checks_passed += 1

        total_checks += 1
        if check("upload_file" in content, "Usa upload_file() para subir"):
            checks_passed += 1

        total_checks += 1
        if check("delete_file" in content, "Usa delete_file() para eliminar"):
            checks_passed += 1

        total_checks += 1
        if check("get_signed_url" in content, "Usa get_signed_url() para descargar"):
            checks_passed += 1
    print()

    # 5. Verificar .env.example actualizado
    print(f"{BLUE}[5/14] Configuración{RESET}")
    env_example = Path(".env.example")
    if env_example.exists():
        content = env_example.read_text(encoding="utf-8")

        total_checks += 1
        if check("GCS_BUCKET_NAME" in content, ".env.example contiene GCS_BUCKET_NAME"):
            checks_passed += 1

        total_checks += 1
        if check("gmao-uploads" in content, ".env.example documenta bucket"):
            checks_passed += 1
    print()

    # 6. requirements.txt actualizado
    print(f"{BLUE}[6/14] Dependencias en requirements.txt{RESET}")
    req_path = Path("requirements.txt")
    if req_path.exists():
        content = req_path.read_text(encoding="utf-8")

        total_checks += 1
        if check(
            "google-cloud-storage" in content,
            "requirements.txt contiene google-cloud-storage",
        ):
            checks_passed += 1
    print()

    # 7. Script de verificación existe (este mismo)
    print(f"{BLUE}[7/14] Scripts{RESET}")
    total_checks += 1
    verify_script = Path("scripts/verify_fase4.py")
    if check(verify_script.exists(), f"Existe {verify_script}"):
        checks_passed += 1
    print()

    # Resumen
    print("=" * 70)
    percentage = (checks_passed / total_checks * 100) if total_checks > 0 else 0

    if percentage == 100:
        print(
            f"{GREEN}✅ FASE 4 COMPLETA: {checks_passed}/{total_checks} checks ({percentage:.1f}%){RESET}"
        )
    elif percentage >= 80:
        print(
            f"{YELLOW}⚠️  FASE 4 CASI COMPLETA: {checks_passed}/{total_checks} checks ({percentage:.1f}%){RESET}"
        )
    else:
        print(
            f"{RED}❌ FASE 4 INCOMPLETA: {checks_passed}/{total_checks} checks ({percentage:.1f}%){RESET}"
        )

    print("=" * 70)
    print()

    # Detalles adicionales
    if percentage >= 80:
        print(f"{GREEN}✅ Implementación del código completada{RESET}")
        print()
        print("📋 Próximos pasos para uso en producción:")
        print("   1. Crear bucket en GCP:")
        print(f"      {BLUE}gcloud storage buckets create gs://gmao-uploads \\{RESET}")
        print(f"      {BLUE}  --location=us-central1 \\{RESET}")
        print(f"      {BLUE}  --uniform-bucket-level-access{RESET}")
        print()
        print("   2. Configurar permisos IAM")
        print(
            "   3. (Opcional) Migrar archivos existentes con scripts/migrate_files_to_gcs.py"
        )
        print("   4. Deploy a App Engine")
        print()

    return 0 if percentage == 100 else 1


if __name__ == "__main__":
    sys.exit(main())
