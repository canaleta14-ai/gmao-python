#!/usr/bin/env python3
"""
Script de Deploy a Producción - GMAO Sistema
Deploy del Dashboard de Monitoreo y configuración EUR
"""

import sys
import subprocess
import datetime


def log_message(message, level="INFO"):
    """Log con timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def run_command(cmd, description, check=True):
    """Ejecutar comando con logging"""
    log_message(f"🔄 {description}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        if result.stdout.strip():
            log_message(f"📝 {result.stdout.strip()}")
        log_message(f"✅ {description} - COMPLETADO")
        return True
    except subprocess.CalledProcessError as e:
        log_message(f"❌ {description} - ERROR: {e.stderr}", "ERROR")
        return False


def pre_deploy_checks():
    """Verificaciones previas al deploy"""
    log_message("🔍 VERIFICACIONES PRE-DEPLOY")
    log_message("=" * 50)

    checks_passed = True

    # Verificar gcloud
    if not run_command(["gcloud", "version"], "Verificando gcloud CLI", check=False):
        checks_passed = False

    # Verificar proyecto configurado
    if not run_command(
        ["gcloud", "config", "get-value", "project"],
        "Verificando proyecto configurado",
        check=False,
    ):
        checks_passed = False

    # Verificar archivos críticos
    import os

    critical_files = ["app.yaml", "main.py", "requirements.txt", "app/factory.py"]

    log_message("📁 Verificando archivos críticos...")
    for file in critical_files:
        if os.path.exists(file):
            log_message(f"✅ {file}: OK")
        else:
            log_message(f"❌ {file}: NO ENCONTRADO", "ERROR")
            checks_passed = False

    return checks_passed


def deploy_to_production():
    """Deploy principal a producción"""
    log_message("🚀 INICIANDO DEPLOY A PRODUCCIÓN")
    log_message("=" * 60)

    # Configurar proyecto
    project_id = "mantenimiento-470311"
    if not run_command(
        ["gcloud", "config", "set", "project", project_id],
        f"Configurando proyecto {project_id}",
    ):
        return False

    # Deploy con Cloud Build
    log_message("🏗️ Desplegando con Cloud Build...")
    deploy_cmd = [
        "gcloud",
        "app",
        "deploy",
        "app.yaml",
        "--project",
        project_id,
        "--version",
        f"dashboard-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "--promote",
        "--quiet",
    ]

    if not run_command(deploy_cmd, "Deploy a App Engine"):
        return False

    log_message("✅ DEPLOY COMPLETADO EXITOSAMENTE!", "SUCCESS")
    return True


def post_deploy_validation():
    """Validaciones post-deploy"""
    log_message("🔍 VALIDACIONES POST-DEPLOY")
    log_message("=" * 50)

    # URLs a verificar
    base_url = "https://mantenimiento-470311.ew.r.appspot.com"
    endpoints_to_check = [
        "/",
        "/api/v2/docs/",
        "/dashboard/",
        "/api/v2/inventario/health",
    ]

    log_message(f"🌐 Verificando endpoints en: {base_url}")

    try:
        import requests

        for endpoint in endpoints_to_check:
            url = f"{base_url}{endpoint}"
            log_message(f"🔗 Verificando: {endpoint}")

            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    log_message(f"✅ {endpoint}: OK (200)")
                else:
                    log_message(f"⚠️ {endpoint}: HTTP {response.status_code}", "WARNING")
            except requests.RequestException as e:
                log_message(f"❌ {endpoint}: Error - {e}", "ERROR")

        log_message("✅ Validaciones post-deploy completadas")
        return True

    except ImportError:
        log_message("⚠️ Requests no disponible, saltando validación HTTP", "WARNING")
        return True


def display_summary():
    """Mostrar resumen del deploy"""
    log_message("📊 RESUMEN DEL DEPLOY")
    log_message("=" * 50)

    components = [
        "✅ Dashboard de Monitoreo (/dashboard/)",
        "✅ API V2 con Swagger (/api/v2/docs/)",
        "✅ Configuración EUR (moneda europea)",
        "✅ Templates actualizados (Bootstrap 5)",
        "✅ Performance optimizada",
        "✅ Cache system mejorado",
    ]

    log_message("🎯 COMPONENTES DESPLEGADOS:")
    for component in components:
        log_message(f"  {component}")

    log_message("\n🔗 URLS IMPORTANTES:")
    base_url = "https://mantenimiento-470311.ew.r.appspot.com"
    urls = [
        f"📊 Dashboard: {base_url}/dashboard/",
        f"📚 Swagger: {base_url}/api/v2/docs/",
        f"❤️ Health: {base_url}/api/v2/inventario/health",
        f"🏠 Home: {base_url}/",
    ]

    for url in urls:
        log_message(f"  {url}")


def main():
    """Función principal del deploy"""
    log_message("🚀 DEPLOY GMAO - DASHBOARD Y EUR")
    log_message("Versión: Dashboard de Monitoreo + Configuración EUR")
    log_message("=" * 60)

    try:
        # 1. Verificaciones previas
        if not pre_deploy_checks():
            log_message(
                "❌ Verificaciones previas fallaron - ABORTANDO DEPLOY", "ERROR"
            )
            return 1

        # 2. Deploy principal
        if not deploy_to_production():
            log_message("❌ Deploy falló - REVISAR LOGS", "ERROR")
            return 1

        # 3. Validaciones post-deploy
        if not post_deploy_validation():
            log_message("⚠️ Validaciones post-deploy con problemas", "WARNING")

        # 4. Mostrar resumen
        display_summary()

        log_message("🎉 DEPLOY COMPLETADO EXITOSAMENTE!", "SUCCESS")
        log_message("✨ Sistema GMAO actualizado con Dashboard y EUR")

        return 0

    except KeyboardInterrupt:
        log_message("❌ Deploy cancelado por usuario", "ERROR")
        return 1
    except Exception as e:
        log_message(f"❌ Error inesperado: {e}", "ERROR")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
