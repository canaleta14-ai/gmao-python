#!/usr/bin/env python
"""
Script de auditoría de seguridad
Verifica configuración de seguridad antes de deployment
"""
import os
import sys
import re
from pathlib import Path


class SecurityAuditor:
    """Auditor de seguridad del proyecto"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.issues = []
        self.warnings = []
        self.passed = []

    def add_issue(self, severity, message):
        """Agregar problema detectado"""
        if severity == "CRITICAL":
            self.issues.append(f"🔴 {message}")
        elif severity == "WARNING":
            self.warnings.append(f"🟡 {message}")
        else:
            self.passed.append(f"✅ {message}")

    def check_env_file(self):
        """Verificar archivo .env"""
        print("\n📋 Verificando archivo .env...")

        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"

        # .env no debe estar en git
        if env_file.exists():
            gitignore = self.project_root / ".gitignore"
            if gitignore.exists():
                content = gitignore.read_text()
                if ".env" in content:
                    self.add_issue("PASS", ".env está en .gitignore")
                else:
                    self.add_issue("CRITICAL", ".env NO está en .gitignore!")

        # .env.example no debe tener credenciales reales
        if env_example.exists():
            content = env_example.read_text()

            # Buscar patrones sospechosos
            suspicious_patterns = [
                (r"dvematimfpjjpxji", "Contraseña real encontrada en .env.example"),
                (r"j_hidalgo@disfood\.com", "Email real encontrado en .env.example"),
                (r"sk-[a-zA-Z0-9]{32,}", "API key de OpenAI encontrada"),
                (r"[a-f0-9]{64}", "Hash/token sospechoso encontrado"),
            ]

            for pattern, message in suspicious_patterns:
                if re.search(pattern, content):
                    self.add_issue("CRITICAL", message)
        else:
            self.add_issue("WARNING", ".env.example no existe")

    def check_secret_key(self):
        """Verificar SECRET_KEY"""
        print("\n🔑 Verificando SECRET_KEY...")

        factory_file = self.project_root / "app" / "factory.py"

        if factory_file.exists():
            content = factory_file.read_text()

            # Verificar que usa Secret Manager en producción
            if "secretmanager" in content:
                self.add_issue("PASS", "Usa Google Secret Manager para producción")
            else:
                self.add_issue(
                    "WARNING", "No usa Secret Manager (puede ser intencional)"
                )

            # Verificar que no hay SECRET_KEY hardcodeada
            if re.search(r'SECRET_KEY\s*=\s*["\'][a-zA-Z0-9]{32,}["\']', content):
                self.add_issue("CRITICAL", "SECRET_KEY hardcodeada en código!")

    def check_csrf_protection(self):
        """Verificar CSRF Protection"""
        print("\n🛡️ Verificando CSRF Protection...")

        extensions_file = self.project_root / "app" / "extensions.py"
        factory_file = self.project_root / "app" / "factory.py"

        if extensions_file.exists():
            content = extensions_file.read_text()
            if "CSRFProtect" in content and "csrf = CSRFProtect()" in content:
                self.add_issue("PASS", "CSRFProtect importado en extensions.py")
            else:
                self.add_issue(
                    "CRITICAL", "CSRFProtect NO configurado en extensions.py"
                )

        if factory_file.exists():
            content = factory_file.read_text()
            if "csrf.init_app(app)" in content:
                self.add_issue("PASS", "CSRF inicializado en factory.py")
            else:
                self.add_issue(
                    "WARNING", "CSRF puede no estar inicializado correctamente"
                )

    def check_rate_limiting(self):
        """Verificar Rate Limiting"""
        print("\n⏱️ Verificando Rate Limiting...")

        extensions_file = self.project_root / "app" / "extensions.py"

        if extensions_file.exists():
            content = extensions_file.read_text()
            if "Limiter" in content and "limiter = Limiter" in content:
                self.add_issue("PASS", "Rate Limiter configurado en extensions.py")
            else:
                self.add_issue("WARNING", "Rate Limiter NO configurado")

        # Verificar que se usa en login
        controllers = list(
            (self.project_root / "app" / "controllers").glob("*_controller.py")
        )
        login_protected = False

        for controller in controllers:
            content = controller.read_text()
            if "login" in content.lower() and "@limiter.limit" in content:
                login_protected = True
                break

        if login_protected:
            self.add_issue("PASS", "Login protegido con rate limiting")
        else:
            self.add_issue(
                "WARNING", "Login puede no estar protegido con rate limiting"
            )

    def check_session_cookies(self):
        """Verificar configuración de cookies de sesión"""
        print("\n🍪 Verificando configuración de cookies...")

        factory_file = self.project_root / "app" / "factory.py"

        if factory_file.exists():
            content = factory_file.read_text()

            checks = [
                ("SESSION_COOKIE_HTTPONLY", "HttpOnly activado"),
                ("SESSION_COOKIE_SAMESITE", "SameSite configurado"),
                ("is_production", "Detección de entorno implementada"),
            ]

            for key, message in checks:
                if key in content:
                    self.add_issue("PASS", message)
                else:
                    self.add_issue("WARNING", f"{message} - NO encontrado")

    def check_sql_injection_protection(self):
        """Verificar protección contra SQL injection"""
        print("\n💉 Verificando protección SQL Injection...")

        # Buscar uso de raw SQL
        model_files = list((self.project_root / "app" / "models").glob("*.py"))
        route_files = list((self.project_root / "app" / "routes").glob("*.py"))

        all_files = model_files + route_files
        raw_sql_found = False

        for file in all_files:
            content = file.read_text()

            # Buscar patrones peligrosos
            dangerous_patterns = [
                r"execute\(f['\"]",  # f-strings en execute
                r"execute\(.*%.*\)",  # string formatting en execute
                r"execute\(.*\+.*\)",  # concatenación en execute
            ]

            for pattern in dangerous_patterns:
                if re.search(pattern, content):
                    raw_sql_found = True
                    self.add_issue("WARNING", f"Posible SQL injection en {file.name}")

        if not raw_sql_found:
            self.add_issue("PASS", "No se encontró SQL raw peligroso")

        # Verificar que se usa SQLAlchemy ORM
        if any("db.session.query" in f.read_text() for f in model_files):
            self.add_issue("PASS", "Usa SQLAlchemy ORM (protección automática)")

    def check_password_hashing(self):
        """Verificar que las contraseñas están hasheadas"""
        print("\n🔒 Verificando hashing de contraseñas...")

        usuario_model = self.project_root / "app" / "models" / "usuario.py"

        if usuario_model.exists():
            content = usuario_model.read_text()

            if "werkzeug.security" in content:
                self.add_issue("PASS", "Usa werkzeug.security para hashing")
            else:
                self.add_issue("CRITICAL", "NO usa librería segura para contraseñas!")

            if "generate_password_hash" in content:
                self.add_issue("PASS", "Función generate_password_hash encontrada")

            if "check_password_hash" in content:
                self.add_issue("PASS", "Función check_password_hash encontrada")

    def check_dependencies(self):
        """Verificar dependencias de seguridad"""
        print("\n📦 Verificando dependencias...")

        requirements = self.project_root / "requirements.txt"

        if requirements.exists():
            content = requirements.read_text()

            security_deps = [
                ("Flask-WTF", "CSRF Protection"),
                ("Flask-Limiter", "Rate Limiting"),
                ("werkzeug", "Password hashing"),
                ("gunicorn", "Servidor de producción"),
            ]

            for dep, purpose in security_deps:
                if dep.lower() in content.lower():
                    self.add_issue("PASS", f"{dep} instalado ({purpose})")
                else:
                    self.add_issue("WARNING", f"{dep} NO instalado ({purpose})")

    def check_debug_mode(self):
        """Verificar que DEBUG está desactivado en producción"""
        print("\n🐛 Verificando modo DEBUG...")

        factory_file = self.project_root / "app" / "factory.py"

        if factory_file.exists():
            content = factory_file.read_text()

            # Buscar app.config["DEBUG"] = True
            if re.search(r'DEBUG["\']?\s*=\s*True', content, re.IGNORECASE):
                self.add_issue("CRITICAL", "DEBUG=True encontrado en código!")
            else:
                self.add_issue("PASS", "DEBUG no está hardcodeado a True")

    def run_audit(self):
        """Ejecutar auditoría completa"""
        print("=" * 60)
        print("🔒 AUDITORÍA DE SEGURIDAD - Sistema GMAO")
        print("=" * 60)

        # Ejecutar todas las verificaciones
        self.check_env_file()
        self.check_secret_key()
        self.check_csrf_protection()
        self.check_rate_limiting()
        self.check_session_cookies()
        self.check_sql_injection_protection()
        self.check_password_hashing()
        self.check_dependencies()
        self.check_debug_mode()

        # Mostrar resultados
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DE AUDITORÍA")
        print("=" * 60)

        if self.passed:
            print(f"\n✅ PASADO ({len(self.passed)}):")
            for item in self.passed:
                print(f"  {item}")

        if self.warnings:
            print(f"\n🟡 ADVERTENCIAS ({len(self.warnings)}):")
            for item in self.warnings:
                print(f"  {item}")

        if self.issues:
            print(f"\n🔴 CRÍTICO ({len(self.issues)}):")
            for item in self.issues:
                print(f"  {item}")

        # Resumen
        print("\n" + "=" * 60)
        print("📈 RESUMEN")
        print("=" * 60)
        print(f"  ✅ Pasado: {len(self.passed)}")
        print(f"  🟡 Advertencias: {len(self.warnings)}")
        print(f"  🔴 Crítico: {len(self.issues)}")

        # Veredicto
        print("\n" + "=" * 60)
        if len(self.issues) == 0:
            if len(self.warnings) == 0:
                print("🎉 SISTEMA SEGURO - Listo para producción")
                return 0
            else:
                print("⚠️  SISTEMA ACEPTABLE - Revisar advertencias antes de producción")
                return 0
        else:
            print(
                "❌ SISTEMA NO SEGURO - Resolver problemas críticos antes de desplegar"
            )
            return 1


def main():
    """Función principal"""
    auditor = SecurityAuditor()
    exit_code = auditor.run_audit()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
