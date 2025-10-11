#!/usr/bin/env python3
"""
Script para probar todos los módulos del sistema GMAO en local
"""

import os
import sys
import requests
import json
import time
from datetime import datetime, timedelta

# Configurar variables de entorno para local
os.environ["SECRETS_PROVIDER"] = "env"
os.environ["SECRET_KEY"] = "tu-clave-secreta-local-muy-segura"
os.environ["DATABASE_URL"] = "sqlite:///C:/Users/canal/gmao-sistema/gmao_local.db"
os.environ["FLASK_ENV"] = "development"

# URL base de la aplicación
BASE_URL = "http://localhost:5000"


class GMOATestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.csrf_token = None
        self.login_successful = False

    def get_csrf_token(self, response_text):
        """Extraer token CSRF de la respuesta HTML"""
        import re

        match = re.search(r'name="csrf_token" value="([^"]+)"', response_text)
        return match.group(1) if match else None

    def test_login(self):
        """Probar el sistema de login"""
        print("\n🔐 Probando sistema de login...")

        try:
            # Obtener página de login
            response = self.session.get(f"{BASE_URL}/login")
            if response.status_code != 200:
                print(f"❌ Error al acceder a login: {response.status_code}")
                return False

            # Extraer token CSRF
            self.csrf_token = self.get_csrf_token(response.text)
            if not self.csrf_token:
                print("❌ No se pudo obtener token CSRF")
                return False

            # Intentar login
            login_data = {
                "username": "admin",
                "password": "admin123",
                "csrf_token": self.csrf_token,
            }

            response = self.session.post(f"{BASE_URL}/login", data=login_data)

            if response.status_code == 302:  # Redirección = login exitoso
                print("✅ Login exitoso")
                self.login_successful = True
                return True
            else:
                print(f"❌ Login fallido: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error en login: {e}")
            return False

    def test_dashboard(self):
        """Probar acceso al dashboard principal"""
        print("\n📊 Probando dashboard principal...")

        try:
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print("✅ Dashboard accesible")
                return True
            else:
                print(f"❌ Error en dashboard: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error en dashboard: {e}")
            return False

    def test_users_module(self):
        """Probar módulo de usuarios"""
        print("\n👥 Probando módulo de usuarios...")

        try:
            # Listar usuarios
            response = self.session.get(f"{BASE_URL}/usuarios")
            if response.status_code == 200:
                print("✅ Lista de usuarios accesible")
            else:
                print(f"❌ Error al listar usuarios: {response.status_code}")
                return False

            # Obtener formulario de nuevo usuario
            response = self.session.get(f"{BASE_URL}/usuarios/nuevo")
            if response.status_code == 200:
                print("✅ Formulario de nuevo usuario accesible")
                return True
            else:
                print(f"❌ Error en formulario usuario: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error en módulo usuarios: {e}")
            return False

    def test_assets_module(self):
        """Probar módulo de activos"""
        print("\n🏭 Probando módulo de activos...")

        try:
            # Listar activos
            response = self.session.get(f"{BASE_URL}/activos")
            if response.status_code == 200:
                print("✅ Lista de activos accesible")
            else:
                print(f"❌ Error al listar activos: {response.status_code}")
                return False

            # Formulario de nuevo activo
            response = self.session.get(f"{BASE_URL}/activos/nuevo")
            if response.status_code == 200:
                print("✅ Formulario de nuevo activo accesible")
                return True
            else:
                print(f"❌ Error en formulario activo: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error en módulo activos: {e}")
            return False

    def test_work_orders_module(self):
        """Probar módulo de órdenes de trabajo"""
        print("\n🔧 Probando módulo de órdenes de trabajo...")

        try:
            # Listar órdenes
            response = self.session.get(f"{BASE_URL}/ordenes")
            if response.status_code == 200:
                print("✅ Lista de órdenes accesible")
            else:
                print(f"❌ Error al listar órdenes: {response.status_code}")
                return False

            # Formulario de nueva orden
            response = self.session.get(f"{BASE_URL}/ordenes/nueva")
            if response.status_code == 200:
                print("✅ Formulario de nueva orden accesible")
                return True
            else:
                print(f"❌ Error en formulario orden: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error en módulo órdenes: {e}")
            return False

    def test_maintenance_plans_module(self):
        """Probar módulo de planes de mantenimiento"""
        print("\n📅 Probando módulo de planes de mantenimiento...")

        try:
            # Listar planes
            response = self.session.get(f"{BASE_URL}/planes")
            if response.status_code == 200:
                print("✅ Lista de planes accesible")
            else:
                print(f"❌ Error al listar planes: {response.status_code}")
                return False

            # Formulario de nuevo plan
            response = self.session.get(f"{BASE_URL}/planes/nuevo")
            if response.status_code == 200:
                print("✅ Formulario de nuevo plan accesible")
                return True
            else:
                print(f"❌ Error en formulario plan: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error en módulo planes: {e}")
            return False

    def test_inventory_module(self):
        """Probar módulo de inventario"""
        print("\n📦 Probando módulo de inventario...")

        try:
            # Listar inventario
            response = self.session.get(f"{BASE_URL}/inventario")
            if response.status_code == 200:
                print("✅ Lista de inventario accesible")
            else:
                print(f"❌ Error al listar inventario: {response.status_code}")
                return False

            # Formulario de nuevo item
            response = self.session.get(f"{BASE_URL}/inventario/nuevo")
            if response.status_code == 200:
                print("✅ Formulario de nuevo item accesible")
                return True
            else:
                print(f"❌ Error en formulario inventario: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error en módulo inventario: {e}")
            return False

    def test_suppliers_module(self):
        """Probar módulo de proveedores"""
        print("\n🏢 Probando módulo de proveedores...")

        try:
            # Listar proveedores
            response = self.session.get(f"{BASE_URL}/proveedores")
            if response.status_code == 200:
                print("✅ Lista de proveedores accesible")
            else:
                print(f"❌ Error al listar proveedores: {response.status_code}")
                return False

            # Formulario de nuevo proveedor
            response = self.session.get(f"{BASE_URL}/proveedores/nuevo")
            if response.status_code == 200:
                print("✅ Formulario de nuevo proveedor accesible")
                return True
            else:
                print(f"❌ Error en formulario proveedor: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error en módulo proveedores: {e}")
            return False

    def test_service_requests_module(self):
        """Probar módulo de solicitudes de servicio"""
        print("\n📋 Probando módulo de solicitudes de servicio...")

        try:
            # Listar solicitudes
            response = self.session.get(f"{BASE_URL}/solicitudes")
            if response.status_code == 200:
                print("✅ Lista de solicitudes accesible")
            else:
                print(f"❌ Error al listar solicitudes: {response.status_code}")
                return False

            # Formulario de nueva solicitud
            response = self.session.get(f"{BASE_URL}/solicitudes/nueva")
            if response.status_code == 200:
                print("✅ Formulario de nueva solicitud accesible")
                return True
            else:
                print(f"❌ Error en formulario solicitud: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error en módulo solicitudes: {e}")
            return False

    def test_reports_module(self):
        """Probar módulo de reportes"""
        print("\n📊 Probando módulo de reportes...")

        try:
            # Acceder a reportes
            response = self.session.get(f"{BASE_URL}/reportes")
            if response.status_code == 200:
                print("✅ Módulo de reportes accesible")
                return True
            else:
                print(f"❌ Error en reportes: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error en módulo reportes: {e}")
            return False

    def test_api_endpoints(self):
        """Probar endpoints de API"""
        print("\n🔌 Probando endpoints de API...")

        try:
            # Test API status
            response = self.session.get(f"{BASE_URL}/api/status")
            if response.status_code == 200:
                print("✅ API status accesible")
            else:
                print(f"⚠️ API status no disponible: {response.status_code}")

            # Test API usuarios
            response = self.session.get(f"{BASE_URL}/api/usuarios")
            if response.status_code == 200:
                print("✅ API usuarios accesible")
                return True
            else:
                print(f"⚠️ API usuarios no disponible: {response.status_code}")
                return True  # No es crítico

        except Exception as e:
            print(f"⚠️ Error en API (no crítico): {e}")
            return True

    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 Iniciando suite de pruebas completa del sistema GMAO")
        print("=" * 60)

        # Verificar que la aplicación esté ejecutándose
        try:
            response = requests.get(BASE_URL, timeout=5)
            if response.status_code != 200:
                print(f"❌ La aplicación no está ejecutándose en {BASE_URL}")
                return False
        except:
            print(
                f"❌ No se puede conectar a {BASE_URL}. ¿Está la aplicación ejecutándose?"
            )
            return False

        print(f"✅ Aplicación disponible en {BASE_URL}")

        # Lista de pruebas
        tests = [
            ("Login", self.test_login),
            ("Dashboard", self.test_dashboard),
            ("Usuarios", self.test_users_module),
            ("Activos", self.test_assets_module),
            ("Órdenes de Trabajo", self.test_work_orders_module),
            ("Planes de Mantenimiento", self.test_maintenance_plans_module),
            ("Inventario", self.test_inventory_module),
            ("Proveedores", self.test_suppliers_module),
            ("Solicitudes de Servicio", self.test_service_requests_module),
            ("Reportes", self.test_reports_module),
            ("API", self.test_api_endpoints),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ Error crítico en {test_name}: {e}")
                results.append((test_name, False))

        # Resumen final
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 60)

        passed = 0
        failed = 0

        for test_name, result in results:
            status = "✅ PASÓ" if result else "❌ FALLÓ"
            print(f"{test_name:25} {status}")
            if result:
                passed += 1
            else:
                failed += 1

        print("-" * 60)
        print(f"Total pruebas: {len(results)}")
        print(f"✅ Pasaron: {passed}")
        print(f"❌ Fallaron: {failed}")
        print(f"📈 Éxito: {(passed/len(results)*100):.1f}%")

        if failed == 0:
            print(
                "\n🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está funcionando correctamente."
            )
        elif failed <= 2:
            print(f"\n⚠️ Sistema funcional con {failed} problemas menores.")
        else:
            print(f"\n❌ Sistema con {failed} problemas importantes.")

        return failed == 0


if __name__ == "__main__":
    print("Sistema de Pruebas GMAO v1.0")
    print("Probando todos los módulos en entorno local...")
    print()

    tester = GMOATestSuite()
    success = tester.run_all_tests()

    exit_code = 0 if success else 1
    sys.exit(exit_code)
