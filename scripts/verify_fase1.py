#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de verificación de seguridad - Versión simplificada
Sistema GMAO - Fase 1
"""
import os
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """Verificar si un archivo existe"""
    if filepath.exists():
        print(f"✅ {description}: {filepath.name}")
        return True
    else:
        print(f"❌ {description}: NO ENCONTRADO")
        return False


def check_in_file(filepath, text, description):
    """Verificar si un texto está en un archivo"""
    try:
        content = filepath.read_text(encoding="utf-8")
        if text in content:
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description}: NO ENCONTRADO")
            return False
    except Exception as e:
        print(f"⚠️  Error leyendo {filepath.name}: {e}")
        return False


def main():
    """Verificación rápida de implementación de Fase 1"""
    print("=" * 60)
    print("🔒 VERIFICACIÓN FASE 1: SEGURIDAD")
    print("=" * 60)

    project_root = Path(__file__).parent.parent
    checks_passed = 0
    total_checks = 0

    # 1. Verificar extensions.py
    print("\n📦 Verificando app/extensions.py...")
    extensions_file = project_root / "app" / "extensions.py"
    total_checks += 3
    checks_passed += check_in_file(
        extensions_file, "CSRFProtect", "CSRFProtect importado"
    )
    checks_passed += check_in_file(
        extensions_file, "csrf = CSRFProtect()", "csrf inicializado"
    )
    checks_passed += check_in_file(extensions_file, "Limiter", "Limiter configurado")

    # 2. Verificar factory.py
    print("\n⚙️  Verificando app/factory.py...")
    factory_file = project_root / "app" / "factory.py"
    total_checks += 3
    checks_passed += check_in_file(
        factory_file, "csrf.init_app(app)", "CSRF inicializado en app"
    )
    checks_passed += check_in_file(
        factory_file, "limiter.init_app(app)", "Limiter inicializado en app"
    )
    checks_passed += check_in_file(
        factory_file, "is_production", "Detección de entorno"
    )

    # 3. Verificar usuarios_controller.py
    print("\n👤 Verificando app/controllers/usuarios_controller.py...")
    controller_file = project_root / "app" / "controllers" / "usuarios_controller.py"
    total_checks += 2
    checks_passed += check_in_file(
        controller_file, "from app.extensions import limiter", "Limiter importado"
    )
    checks_passed += check_in_file(
        controller_file, "@limiter.limit", "Rate limiting aplicado"
    )

    # 4. Verificar requirements.txt
    print("\n📋 Verificando requirements.txt...")
    requirements_file = project_root / "requirements.txt"
    total_checks += 2
    checks_passed += check_in_file(
        requirements_file, "Flask-WTF", "Flask-WTF en requirements"
    )
    checks_passed += check_in_file(
        requirements_file, "Flask-Limiter", "Flask-Limiter en requirements"
    )

    # 5. Verificar tests
    print("\n🧪 Verificando tests...")
    test_file = project_root / "tests" / "test_security.py"
    total_checks += 1
    checks_passed += check_file_exists(test_file, "Tests de seguridad")

    # 6. Verificar .env.example
    print("\n🔐 Verificando .env.example...")
    env_example = project_root / ".env.example"
    try:
        content = env_example.read_text(encoding="utf-8")
        total_checks += 1
        if "dvematimfpjjpxji" not in content:
            print("✅ Credenciales sensibles eliminadas")
            checks_passed += 1
        else:
            print("❌ CRÍTICO: Credenciales aún expuestas!")
    except Exception as e:
        print(f"⚠️  Error verificando .env.example: {e}")

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    percentage = (checks_passed / total_checks) * 100 if total_checks > 0 else 0
    print(f"Checks pasados: {checks_passed}/{total_checks} ({percentage:.1f}%)")

    if checks_passed == total_checks:
        print("\n✅ FASE 1 IMPLEMENTADA CORRECTAMENTE")
        print("Siguiente paso: Instalar dependencias y ejecutar tests")
        print("\nComandos:")
        print("  pip install Flask-WTF Flask-Limiter")
        print("  pytest tests/test_security.py -v")
        return 0
    elif checks_passed >= total_checks * 0.8:
        print("\n⚠️  FASE 1 CASI COMPLETA")
        print("Revisar checks fallidos arriba")
        return 0
    else:
        print("\n❌ FASE 1 INCOMPLETA")
        print("Revisar implementación")
        return 1


if __name__ == "__main__":
    sys.exit(main())
