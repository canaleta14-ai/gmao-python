"""
Script de verificación pre-deployment
Verifica que todo está listo para deployment a GCP
"""

import os
import sys
from pathlib import Path


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")


def check_mark(passed):
    return (
        f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"
    )


def check_file_exists(filepath, description):
    """Verifica que un archivo existe"""
    exists = Path(filepath).exists()
    status = check_mark(exists)
    print(f"{status} {description}: {filepath}")
    return exists


def check_package_installed(package_name):
    """Verifica que un paquete Python está instalado"""
    try:
        __import__(package_name.replace("-", "_"))
        print(f"{Colors.GREEN}✓{Colors.RESET} {package_name} instalado")
        return True
    except ImportError:
        print(f"{Colors.RED}✗{Colors.RESET} {package_name} NO instalado")
        return False


def check_env_var(var_name, optional=False):
    """Verifica que una variable de entorno existe"""
    exists = var_name in os.environ
    if optional:
        status = (
            f"{Colors.YELLOW}○{Colors.RESET}"
            if not exists
            else f"{Colors.GREEN}✓{Colors.RESET}"
        )
        opt_text = " (opcional)" if not exists else ""
        print(f"{status} Variable {var_name}{opt_text}")
    else:
        status = check_mark(exists)
        print(
            f"{status} Variable {var_name} {'configurada' if exists else 'NO configurada'}"
        )
    return exists or optional


def main():
    print_header("VERIFICACIÓN PRE-DEPLOYMENT - GMAO Sistema")

    all_checks_passed = True

    # 1. Verificar archivos esenciales
    print(f"\n{Colors.BOLD}1. Archivos Esenciales{Colors.RESET}")
    print("-" * 70)

    files_to_check = [
        ("app.yaml", "Configuración App Engine"),
        ("requirements.txt", "Dependencias Python"),
        ("run.py", "Punto de entrada de la aplicación"),
        ("cron.yaml", "Configuración de cron jobs"),
        (".coveragerc", "Configuración de coverage"),
        ("pytest.ini", "Configuración de pytest"),
    ]

    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_checks_passed = False

    # 2. Verificar estructura de directorios
    print(f"\n{Colors.BOLD}2. Estructura de Directorios{Colors.RESET}")
    print("-" * 70)

    dirs_to_check = [
        "app",
        "app/models",
        "app/routes",
        "app/controllers",
        "app/templates",
        "static",
        "tests",
        ".github/workflows",
    ]

    for dir_path in dirs_to_check:
        exists = Path(dir_path).is_dir()
        status = check_mark(exists)
        print(f"{status} Directorio {dir_path} {'existe' if exists else 'NO existe'}")
        if not exists:
            all_checks_passed = False

    # 3. Verificar paquetes críticos
    print(f"\n{Colors.BOLD}3. Paquetes Python Críticos{Colors.RESET}")
    print("-" * 70)

    critical_packages = [
        "flask",
        "gunicorn",
        "psycopg2",
        "sqlalchemy",
        "flask_sqlalchemy",
        "flask_login",
        "flask_migrate",
        "google.cloud.secretmanager",
        "google.cloud.storage",
    ]

    for package in critical_packages:
        if not check_package_installed(package):
            all_checks_passed = False

    # 4. Verificar configuración en app.yaml
    print(f"\n{Colors.BOLD}4. Verificar app.yaml{Colors.RESET}")
    print("-" * 70)

    if Path("app.yaml").exists():
        with open("app.yaml", "r", encoding="utf-8") as f:
            content = f.read()

        checks = [
            ("runtime: python311" in content, "Runtime Python 3.11"),
            ("gunicorn" in content, "Gunicorn configurado"),
            ("cloud_sql_instances" in content, "Cloud SQL configurado"),
            ("handlers:" in content, "Handlers configurados"),
            (
                "/health" in content or "health_check" in content,
                "Health check configurado",
            ),
        ]

        for check, description in checks:
            status = check_mark(check)
            print(f"{status} {description}")
            if not check:
                all_checks_passed = False
    else:
        print(f"{Colors.RED}✗ app.yaml no encontrado{Colors.RESET}")
        all_checks_passed = False

    # 5. Verificar variables de entorno (opcional para local)
    print(f"\n{Colors.BOLD}5. Variables de Entorno (Local - Opcional){Colors.RESET}")
    print("-" * 70)

    env_vars = [
        ("FLASK_APP", True),
        ("FLASK_ENV", True),
        ("SECRET_KEY", True),
        ("DATABASE_URL", True),
        ("GOOGLE_APPLICATION_CREDENTIALS", True),
    ]

    for var, optional in env_vars:
        check_env_var(var, optional)

    # 6. Verificar que tests pasan
    print(f"\n{Colors.BOLD}6. Estado de Tests{Colors.RESET}")
    print("-" * 70)

    try:
        import subprocess

        result = subprocess.run(
            ["pytest", "tests/", "-v", "--tb=no", "-q"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if "passed" in result.stdout:
            # Extraer número de tests pasando
            import re

            match = re.search(r"(\d+) passed", result.stdout)
            if match:
                passed_tests = match.group(1)
                print(
                    f"{Colors.GREEN}✓{Colors.RESET} Tests ejecutados: {passed_tests} pasando"
                )
        else:
            print(f"{Colors.YELLOW}○{Colors.RESET} No se pudieron ejecutar tests")
    except Exception as e:
        print(f"{Colors.YELLOW}○{Colors.RESET} Tests no ejecutados: {e}")

    # 7. Verificar archivos sensibles NO incluidos
    print(f"\n{Colors.BOLD}7. Seguridad - Archivos Sensibles{Colors.RESET}")
    print("-" * 70)

    gitignore_exists = Path(".gitignore").exists()
    status = check_mark(gitignore_exists)
    print(f"{status} .gitignore {'existe' if gitignore_exists else 'NO existe'}")

    if gitignore_exists:
        with open(".gitignore", "r") as f:
            gitignore_content = f.read()

        sensitive_patterns = [
            (".env", "Archivos .env"),
            ("*.pyc", "Archivos .pyc"),
            ("__pycache__", "Directorios __pycache__"),
            ("instance/", "Directorio instance/"),
            (".venv", "Entorno virtual"),
        ]

        for pattern, description in sensitive_patterns:
            is_ignored = pattern in gitignore_content
            status = check_mark(is_ignored)
            print(
                f"{status} {description} {'en .gitignore' if is_ignored else 'NO en .gitignore'}"
            )

    # 8. Verificar migraciones
    print(f"\n{Colors.BOLD}8. Migraciones de Base de Datos{Colors.RESET}")
    print("-" * 70)

    migrations_dir = Path("migrations/versions")
    if migrations_dir.exists():
        migrations = list(migrations_dir.glob("*.py"))
        migrations = [m for m in migrations if not m.name.startswith("__")]
        print(
            f"{Colors.GREEN}✓{Colors.RESET} {len(migrations)} migraciones encontradas"
        )

        if migrations:
            print(f"\n  Últimas 3 migraciones:")
            for migration in sorted(migrations, reverse=True)[:3]:
                print(f"    - {migration.name}")
    else:
        print(f"{Colors.YELLOW}○{Colors.RESET} Directorio de migraciones no encontrado")

    # Resumen final
    print("\n" + "=" * 70)
    if all_checks_passed:
        print(
            f"{Colors.GREEN}{Colors.BOLD}✓ TODAS LAS VERIFICACIONES PASARON{Colors.RESET}"
        )
        print(f"\n{Colors.GREEN}Sistema listo para deployment a GCP{Colors.RESET}")
        print("\nPróximos pasos:")
        print("1. Instalar Google Cloud SDK si no lo tienes")
        print("2. Ejecutar: gcloud auth login")
        print("3. Seguir DEPLOYMENT_GUIDE.md")
        return 0
    else:
        print(
            f"{Colors.YELLOW}{Colors.BOLD}⚠ ALGUNAS VERIFICACIONES FALLARON{Colors.RESET}"
        )
        print(
            f"\n{Colors.YELLOW}Revisa los items marcados con ✗ antes de continuar{Colors.RESET}"
        )
        print(
            "\nPuedes continuar con deployment, pero algunos issues pueden causar problemas."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
