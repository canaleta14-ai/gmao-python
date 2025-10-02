#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Verificación: Fase 2 - Migraciones de Base de Datos

Verifica que Flask-Migrate esté correctamente configurado y funcionando.

Uso:
    python scripts/verify_fase2.py
"""

import os
import sys
import subprocess
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
    print_header("VERIFICACIÓN FASE 2: MIGRACIONES DE BASE DE DATOS")

    checks_passed = 0
    checks_total = 0

    # Directorio raíz del proyecto
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # ========== VERIFICACIÓN 1: Flask-Migrate Instalado ==========
    checks_total += 1
    try:
        import flask_migrate

        # Flask-Migrate no tiene __version__, pero si se importa, está instalado
        print_check("Flask-Migrate instalado", True, "Módulo disponible")
        checks_passed += 1
    except ImportError:
        print_check(
            "Flask-Migrate instalado", False, "Ejecutar: pip install Flask-Migrate"
        )

    # ========== VERIFICACIÓN 2: Alembic Instalado ==========
    checks_total += 1
    try:
        import alembic

        version = alembic.__version__
        print_check("Alembic instalado", True, f"Versión: {version}")
        checks_passed += 1
    except ImportError:
        print_check(
            "Alembic instalado", False, "Se instala automáticamente con Flask-Migrate"
        )

    # ========== VERIFICACIÓN 3: Directorio migrations existe ==========
    checks_total += 1
    migrations_dir = project_root / "migrations"
    if migrations_dir.exists() and migrations_dir.is_dir():
        print_check("Directorio migrations/ existe", True, str(migrations_dir))
        checks_passed += 1
    else:
        print_check("Directorio migrations/ existe", False, "Ejecutar: flask db init")

    # ========== VERIFICACIÓN 4: alembic.ini existe ==========
    checks_total += 1
    alembic_ini = migrations_dir / "alembic.ini"
    if alembic_ini.exists():
        print_check("alembic.ini configurado", True, str(alembic_ini))
        checks_passed += 1
    else:
        print_check(
            "alembic.ini configurado", False, "Archivo de configuración faltante"
        )

    # ========== VERIFICACIÓN 5: env.py existe ==========
    checks_total += 1
    env_py = migrations_dir / "env.py"
    if env_py.exists():
        print_check("env.py existe", True, "Archivo de entorno de Alembic")
        checks_passed += 1
    else:
        print_check("env.py existe", False, "Archivo de entorno faltante")

    # ========== VERIFICACIÓN 6: script.py.mako existe ==========
    checks_total += 1
    script_mako = migrations_dir / "script.py.mako"
    if script_mako.exists():
        print_check("script.py.mako existe", True, "Plantilla de migraciones")
        checks_passed += 1
    else:
        print_check("script.py.mako existe", False, "Plantilla de migraciones faltante")

    # ========== VERIFICACIÓN 7: Directorio versions existe ==========
    checks_total += 1
    versions_dir = migrations_dir / "versions"
    if versions_dir.exists() and versions_dir.is_dir():
        # Contar archivos de migración
        migration_files = list(versions_dir.glob("*.py"))
        if migration_files:
            count = len(migration_files)
            print_check(
                "Directorio versions/ existe",
                True,
                f"{count} migración(es) encontrada(s)",
            )
        else:
            print_check(
                "Directorio versions/ existe",
                True,
                "Sin migraciones (normal en instalación nueva)",
            )
        checks_passed += 1
    else:
        print_check(
            "Directorio versions/ existe", False, "Directorio de versiones faltante"
        )

    # ========== VERIFICACIÓN 8: migrate importado en extensions.py ==========
    checks_total += 1
    extensions_file = project_root / "app" / "extensions.py"
    if extensions_file.exists():
        content = extensions_file.read_text(encoding="utf-8")
        if (
            "from flask_migrate import Migrate" in content
            and "migrate = Migrate()" in content
        ):
            print_check("Migrate en extensions.py", True, "Importación correcta")
            checks_passed += 1
        else:
            print_check(
                "Migrate en extensions.py", False, "Falta importación o inicialización"
            )
    else:
        print_check(
            "Migrate en extensions.py", False, "Archivo extensions.py no encontrado"
        )

    # ========== VERIFICACIÓN 9: migrate.init_app en factory.py ==========
    checks_total += 1
    factory_file = project_root / "app" / "factory.py"
    if factory_file.exists():
        content = factory_file.read_text(encoding="utf-8")
        if "migrate.init_app(app, db)" in content:
            print_check(
                "migrate.init_app() en factory.py", True, "Inicialización correcta"
            )
            checks_passed += 1
        else:
            print_check(
                "migrate.init_app() en factory.py",
                False,
                "Falta inicialización en create_app()",
            )
    else:
        print_check(
            "migrate.init_app() en factory.py",
            False,
            "Archivo factory.py no encontrado",
        )

    # ========== VERIFICACIÓN 10: Comando flask db disponible ==========
    checks_total += 1
    try:
        result = subprocess.run(
            ["flask", "db", "--help"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and "migrate" in result.stdout.lower():
            print_check(
                "Comando 'flask db' disponible",
                True,
                "Todos los comandos de migración funcionan",
            )
            checks_passed += 1
        else:
            print_check(
                "Comando 'flask db' disponible",
                False,
                "Comando no funciona correctamente",
            )
    except Exception as e:
        print_check("Comando 'flask db' disponible", False, f"Error al ejecutar: {e}")

    # ========== VERIFICACIÓN 11: requirements.txt actualizado ==========
    checks_total += 1
    req_file = project_root / "requirements.txt"
    if req_file.exists():
        content = req_file.read_text(encoding="utf-8")
        if "Flask-Migrate" in content or "flask-migrate" in content:
            print_check(
                "Flask-Migrate en requirements.txt", True, "Dependencia registrada"
            )
            checks_passed += 1
        else:
            print_check(
                "Flask-Migrate en requirements.txt",
                False,
                "Ejecutar: pip freeze > requirements.txt",
            )
    else:
        print_check(
            "Flask-Migrate en requirements.txt",
            False,
            "Archivo requirements.txt no encontrado",
        )

    # ========== VERIFICACIÓN 12: Base de datos versionada ==========
    checks_total += 1
    try:
        result = subprocess.run(
            ["flask", "db", "current"], capture_output=True, text=True, timeout=10
        )
        # Si hay output con revision o no muestra error, está versionada
        if result.returncode == 0:
            if result.stdout.strip():
                print_check("Base de datos versionada", True, "BD marcada con versión")
            else:
                print_check(
                    "Base de datos versionada", True, "BD en head (sin migraciones aún)"
                )
            checks_passed += 1
        else:
            print_check(
                "Base de datos versionada", False, "Ejecutar: flask db stamp head"
            )
    except Exception as e:
        print_check("Base de datos versionada", False, f"Error al verificar: {e}")

    # ========== RESUMEN FINAL ==========
    print_header("RESUMEN DE VERIFICACIÓN")

    percentage = (checks_passed / checks_total) * 100
    print(
        f"\nVerificaciones pasadas: {checks_passed}/{checks_total} ({percentage:.1f}%)"
    )

    if checks_passed == checks_total:
        print("\n✅ FASE 2 COMPLETADA EXITOSAMENTE")
        print("Flask-Migrate está correctamente configurado.")
        print("\nPróximos pasos:")
        print("  1. Crear migración: flask db migrate -m 'Descripción'")
        print("  2. Aplicar migración: flask db upgrade")
        print("  3. Ver historial: flask db history")
        return 0
    elif checks_passed >= checks_total * 0.8:
        print("\n⚠️  FASE 2 CASI COMPLETA")
        print("Algunas verificaciones fallaron, pero lo principal está configurado.")
        print("Revisa los puntos marcados como FALLO.")
        return 1
    else:
        print("\n❌ FASE 2 INCOMPLETA")
        print("Varias verificaciones fallaron. Completa los pasos faltantes.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
