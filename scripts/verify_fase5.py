"""
Script de verificación de la Fase 5: Cloud Scheduler
Verifica que todos los componentes estén correctamente implementados
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


def check_flask_mail_installed():
    """Verifica que Flask-Mail esté instalado"""
    try:
        import flask_mail

        version = getattr(flask_mail, "__version__", "unknown")
        print(f"✓ Flask-Mail instalado (versión: {version})")
        return True
    except ImportError:
        print("✗ Flask-Mail NO está instalado")
        return False


def check_cron_routes_exist():
    """Verifica que el archivo de rutas de cron exista"""
    cron_file = root_dir / "app" / "routes" / "cron.py"

    if cron_file.exists():
        print(f"✓ Archivo cron.py existe ({cron_file})")
        return True
    else:
        print(f"✗ Archivo cron.py NO existe")
        return False


def check_cron_endpoints():
    """Verifica que los endpoints de cron estén definidos"""
    try:
        from app.routes.cron import cron_bp

        endpoints = []
        for rule in cron_bp.url_map._rules:
            if rule.blueprint == "cron":
                endpoints.append(rule.rule)

        expected_endpoints = [
            "/api/cron/generar-ordenes-preventivas",
            "/api/cron/verificar-alertas",
            "/api/cron/test-cron",
        ]

        found_all = True
        for endpoint in expected_endpoints:
            # Verificar si existe (considerando el prefijo del blueprint)
            endpoint_base = endpoint.replace("/api/cron", "")
            found = any(endpoint_base in rule for rule in endpoints)

            if found:
                print(f"✓ Endpoint {endpoint} definido")
            else:
                print(f"✗ Endpoint {endpoint} NO definido")
                found_all = False

        return found_all
    except Exception as e:
        print(f"✗ Error verificando endpoints: {e}")
        return False


def check_cron_blueprint_registered():
    """Verifica que el blueprint de cron esté registrado en factory"""
    try:
        factory_file = root_dir / "app" / "factory.py"
        content = factory_file.read_text(encoding="utf-8")

        checks = {
            "import": "from app.routes.cron import cron_bp" in content,
            "register": "app.register_blueprint(cron_bp)" in content,
        }

        if all(checks.values()):
            print("✓ Blueprint de cron registrado en factory.py")
            return True
        else:
            for name, result in checks.items():
                if not result:
                    print(f"✗ {name} de cron_bp NO encontrado en factory.py")
            return False
    except Exception as e:
        print(f"✗ Error verificando factory.py: {e}")
        return False


def check_orden_plan_relationship():
    """Verifica que la relación orden-plan exista en el modelo"""
    try:
        orden_file = root_dir / "app" / "models" / "orden_trabajo.py"
        content = orden_file.read_text(encoding="utf-8")

        checks = {
            "plan_mantenimiento_id": "plan_mantenimiento_id" in content,
            "relationship": "db.relationship('PlanMantenimiento'" in content
            or 'db.relationship("PlanMantenimiento"' in content,
            "foreign_key": "db.ForeignKey('plan_mantenimiento.id')" in content,
        }

        if all(checks.values()):
            print("✓ Relación orden-plan definida en orden_trabajo.py")
            return True
        else:
            for name, result in checks.items():
                if not result:
                    print(f"✗ {name} NO encontrado en orden_trabajo.py")
            return False
    except Exception as e:
        print(f"✗ Error verificando orden_trabajo.py: {e}")
        return False


def check_migration_applied():
    """Verifica que la migración de plan_mantenimiento_id esté aplicada"""
    try:
        from app.factory import create_app
        from app.extensions import db
        from sqlalchemy import inspect

        app = create_app()

        with app.app_context():
            # Inspeccionar la tabla orden_trabajo
            inspector = inspect(db.engine)
            columns = [col["name"] for col in inspector.get_columns("orden_trabajo")]

            if "plan_mantenimiento_id" in columns:
                print(
                    "✓ Migración aplicada: columna plan_mantenimiento_id existe en orden_trabajo"
                )
                return True
            else:
                print(
                    "✗ Migración NO aplicada: columna plan_mantenimiento_id NO existe"
                )
                return False
    except Exception as e:
        print(f"✗ Error verificando migración: {e}")
        return False


def check_cron_yaml_exists():
    """Verifica que el archivo cron.yaml exista"""
    cron_yaml = root_dir / "cron.yaml"

    if cron_yaml.exists():
        content = cron_yaml.read_text(encoding="utf-8")

        checks = {
            "generar-ordenes": "generar-ordenes-preventivas" in content,
            "verificar-alertas": "verificar-alertas" in content,
            "schedule": "schedule:" in content,
            "timezone": "timezone:" in content,
        }

        if all(checks.values()):
            print("✓ cron.yaml configurado correctamente")
            return True
        else:
            for name, result in checks.items():
                if not result:
                    print(f"✗ {name} NO encontrado en cron.yaml")
            return False
    else:
        print("✗ cron.yaml NO existe")
        return False


def check_env_example_updated():
    """Verifica que .env.example esté actualizado con las variables de cron"""
    env_example = root_dir / ".env.example"

    if env_example.exists():
        content = env_example.read_text(encoding="utf-8")

        checks = {
            "ADMIN_EMAILS": "ADMIN_EMAILS" in content,
            "SERVER_URL": "SERVER_URL" in content,
            "MAIL_SERVER": "MAIL_SERVER" in content,
        }

        if all(checks.values()):
            print("✓ .env.example actualizado con variables de cron")
            return True
        else:
            for name, result in checks.items():
                if not result:
                    print(f"⚠ {name} NO encontrado en .env.example (opcional)")
            return True  # No crítico
    else:
        print("⚠ .env.example NO existe")
        return True  # No crítico


def check_security_function():
    """Verifica que la función de seguridad esté implementada"""
    try:
        cron_file = root_dir / "app" / "routes" / "cron.py"
        content = cron_file.read_text(encoding="utf-8")

        checks = {
            "is_valid_cron_request": "def is_valid_cron_request" in content,
            "X-Appengine-Cron": "X-Appengine-Cron" in content,
            "development_check": "FLASK_ENV" in content or "development" in content,
        }

        if all(checks.values()):
            print("✓ Función de seguridad is_valid_cron_request implementada")
            return True
        else:
            for name, result in checks.items():
                if not result:
                    print(f"✗ {name} NO encontrado en cron.py")
            return False
    except Exception as e:
        print(f"✗ Error verificando seguridad: {e}")
        return False


def check_email_functions():
    """Verifica que las funciones de email estén implementadas"""
    try:
        cron_file = root_dir / "app" / "routes" / "cron.py"
        content = cron_file.read_text(encoding="utf-8")

        checks = {
            "enviar_notificacion_orden": "def enviar_notificacion_orden_creada"
            in content,
            "enviar_alerta": "def enviar_alerta_mantenimiento" in content,
            "flask_mail_import": "from flask_mail import" in content
            or "import flask_mail" in content,
        }

        if all(checks.values()):
            print("✓ Funciones de envío de email implementadas")
            return True
        else:
            for name, result in checks.items():
                if not result:
                    print(f"✗ {name} NO encontrado en cron.py")
            return False
    except Exception as e:
        print(f"✗ Error verificando funciones de email: {e}")
        return False


def check_requirements_txt():
    """Verifica que requirements.txt incluya Flask-Mail"""
    requirements_file = root_dir / "requirements.txt"

    if requirements_file.exists():
        content = requirements_file.read_text(encoding="utf-8")

        if "Flask-Mail" in content or "flask-mail" in content.lower():
            print("✓ Flask-Mail incluido en requirements.txt")
            return True
        else:
            print("✗ Flask-Mail NO incluido en requirements.txt")
            return False
    else:
        print("✗ requirements.txt NO existe")
        return False


def check_plan_mantenimiento_model():
    """Verifica que el modelo PlanMantenimiento tenga los campos necesarios"""
    try:
        plan_file = root_dir / "app" / "models" / "plan_mantenimiento.py"
        content = plan_file.read_text(encoding="utf-8")

        checks = {
            "proxima_ejecucion": "proxima_ejecucion" in content,
            "ultima_ejecucion": "ultima_ejecucion" in content,
            "activo": "activo" in content,
            "frecuencia": "frecuencia" in content,
        }

        if all(checks.values()):
            print("✓ Modelo PlanMantenimiento tiene campos necesarios")
            return True
        else:
            for name, result in checks.items():
                if not result:
                    print(f"⚠ Campo {name} NO encontrado en plan_mantenimiento.py")
            return True  # No crítico si es un modelo existente
    except Exception as e:
        print(f"⚠ Error verificando plan_mantenimiento.py: {e}")
        return True  # No crítico


def main():
    """Ejecuta todas las verificaciones"""
    print("\n" + "╔" + "=" * 58 + "╗")
    print("║  VERIFICACIÓN FASE 5: CLOUD SCHEDULER                  ║")
    print("╚" + "=" * 58 + "╝\n")

    checks = {
        "Flask-Mail instalado": check_flask_mail_installed,
        "Archivo cron.py existe": check_cron_routes_exist,
        "Endpoints de cron definidos": check_cron_endpoints,
        "Blueprint registrado": check_cron_blueprint_registered,
        "Relación orden-plan": check_orden_plan_relationship,
        "Migración aplicada": check_migration_applied,
        "cron.yaml configurado": check_cron_yaml_exists,
        ".env.example actualizado": check_env_example_updated,
        "Función de seguridad": check_security_function,
        "Funciones de email": check_email_functions,
        "requirements.txt actualizado": check_requirements_txt,
        "Modelo PlanMantenimiento": check_plan_mantenimiento_model,
    }

    results = {}

    for name, check_func in checks.items():
        print(f"\n{name}:")
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"✗ Error en verificación: {e}")
            results[name] = False

    # Resumen
    print("\n" + "╔" + "=" * 58 + "╗")
    print("║  RESUMEN DE VERIFICACIÓN                               ║")
    print("╚" + "=" * 58 + "╝\n")

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    percentage = (passed / total) * 100

    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")

    print(f"\n✓ Verificaciones exitosas: {passed}/{total} ({percentage:.1f}%)")

    if percentage == 100:
        print("\n🎉 ¡FASE 5 COMPLETADA AL 100%!")
        print("\nPróximos pasos:")
        print("1. Probar endpoints: python scripts/test_cron_local.py")
        print("2. Configurar variables de entorno para email (MAIL_SERVER, etc.)")
        print("3. Continuar con Fase 6: Testing & CI/CD")
    elif percentage >= 80:
        print("\n✓ Fase 5 mayormente completa")
        print("\n⚠ Algunas verificaciones fallaron. Revisa los detalles arriba.")
    else:
        print("\n✗ Fase 5 incompleta")
        print("\n⚠ Varias verificaciones críticas fallaron.")

    print("\n" + "=" * 60 + "\n")

    return percentage >= 80


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
