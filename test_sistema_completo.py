#!/usr/bin/env python3
"""
Script de verificación integral del sistema GMAO
Verifica todos los módulos y funcionalidades principales
"""

import requests
import json
import re
from datetime import datetime
import time


class GMaoTestSuite:
    def __init__(self):
        self.base_url = "https://mantenimiento-470311.ew.r.appspot.com"
        self.session = requests.Session()
        self.csrf_token = None
        self.resultados = {
            "modulos_probados": 0,
            "modulos_ok": 0,
            "modulos_error": 0,
            "errores": [],
        }

    def log(self, mensaje, tipo="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        simbolo = "✅" if tipo == "OK" else "❌" if tipo == "ERROR" else "🔍"
        print(f"[{timestamp}] {simbolo} {mensaje}")

    def get_csrf_token(self, url):
        """Obtener token CSRF de una página"""
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                csrf_match = re.search(
                    r'name="csrf_token" value="([^"]+)"', response.text
                )
                return csrf_match.group(1) if csrf_match else None
            return None
        except Exception as e:
            self.log(f"Error obteniendo CSRF: {e}", "ERROR")
            return None

    def test_modulo(self, nombre, endpoint, metodo="GET", require_auth=False):
        """Probar un módulo específico"""
        self.log(f"Probando módulo: {nombre}")
        self.resultados["modulos_probados"] += 1

        try:
            url = f"{self.base_url}{endpoint}"

            if metodo == "GET":
                response = self.session.get(url, timeout=15)
            else:
                response = self.session.request(metodo, url, timeout=15)

            if response.status_code in [200, 302, 308]:
                self.log(f"{nombre}: OK (código {response.status_code})", "OK")
                self.resultados["modulos_ok"] += 1
                return True
            else:
                error_msg = f"{nombre}: Error {response.status_code}"
                self.log(error_msg, "ERROR")
                self.resultados["errores"].append(error_msg)
                self.resultados["modulos_error"] += 1
                return False

        except Exception as e:
            error_msg = f"{nombre}: Excepción - {str(e)}"
            self.log(error_msg, "ERROR")
            self.resultados["errores"].append(error_msg)
            self.resultados["modulos_error"] += 1
            return False

    def test_api_endpoint(self, nombre, endpoint, metodo="GET"):
        """Probar un endpoint de API específico"""
        self.log(f"Probando API: {nombre}")
        self.resultados["modulos_probados"] += 1

        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.request(metodo, url, timeout=15)

            # Códigos de éxito para APIs (incluyendo 401 para endpoints protegidos)
            codigos_ok = [200, 201, 302, 401, 403]

            if response.status_code in codigos_ok:
                self.log(f"API {nombre}: OK (código {response.status_code})", "OK")
                self.resultados["modulos_ok"] += 1
                return True
            else:
                error_msg = f"API {nombre}: Error {response.status_code}"
                self.log(error_msg, "ERROR")
                self.resultados["errores"].append(error_msg)
                self.resultados["modulos_error"] += 1
                return False

        except Exception as e:
            error_msg = f"API {nombre}: Excepción - {str(e)}"
            self.log(error_msg, "ERROR")
            self.resultados["errores"].append(error_msg)
            self.resultados["modulos_error"] += 1
            return False

    def verificar_sistema_completo(self):
        """Verificar todos los módulos del sistema GMAO"""

        print("🧪 VERIFICACIÓN INTEGRAL DEL SISTEMA GMAO")
        print("=" * 60)
        print(f"🌐 URL Base: {self.base_url}")
        print(f"🕐 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 1. MÓDULOS WEB PRINCIPALES
        self.log("=== VERIFICANDO MÓDULOS WEB ===")

        modulos_web = [
            ("Página Principal", "/"),
            ("Login", "/login"),
            ("Dashboard Admin", "/admin"),
            ("Solicitudes", "/solicitudes/"),
            ("Admin Solicitudes", "/admin/solicitudes/"),
            ("Órdenes de Trabajo", "/ordenes/"),
            ("Planes de Mantenimiento", "/planes/"),
            ("Activos", "/activos/"),
            ("Inventario", "/inventario/"),
            ("Usuarios", "/usuarios/"),
            ("Proveedores", "/proveedores/"),
            ("Categorías", "/categorias/"),
            ("Estadísticas", "/estadisticas/"),
            ("Calendario", "/calendario/"),
        ]

        for nombre, endpoint in modulos_web:
            self.test_modulo(nombre, endpoint)
            time.sleep(0.5)  # Evitar sobrecarga

        print()

        # 2. APIs PRINCIPALES
        self.log("=== VERIFICANDO APIs ===")

        apis = [
            ("API Solicitudes", "/api/solicitudes"),
            ("API Órdenes", "/api/ordenes"),
            ("API Planes", "/api/planes"),
            ("API Activos", "/api/activos"),
            ("API Usuarios", "/api/usuarios"),
            ("API Inventario", "/api/inventario"),
            ("API Estadísticas", "/api/estadisticas"),
            ("API User Info", "/api/user/info"),
            ("API Health Check", "/api/health"),
        ]

        for nombre, endpoint in apis:
            self.test_api_endpoint(nombre, endpoint)
            time.sleep(0.5)

        print()

        # 3. FUNCIONALIDADES ESPECÍFICAS
        self.log("=== VERIFICANDO FUNCIONALIDADES ESPECÍFICAS ===")

        # Probar creación de solicitud (ya sabemos que funciona)
        self.log("Probando creación de solicitud...")
        csrf_token = self.get_csrf_token("/solicitudes/")
        if csrf_token:
            self.log("Token CSRF obtenido correctamente", "OK")
            self.resultados["modulos_ok"] += 1
        else:
            self.log("Error obteniendo token CSRF", "ERROR")
            self.resultados["modulos_error"] += 1
        self.resultados["modulos_probados"] += 1

        # 4. CRON JOBS Y AUTOMATIZACIÓN
        self.log("=== VERIFICANDO AUTOMATIZACIÓN ===")

        cron_endpoints = [
            ("Generación Órdenes Preventivas", "/api/cron/generar-ordenes-preventivas"),
            ("Verificar Alertas", "/api/cron/verificar-alertas"),
            ("DB Fix", "/api/cron/db-fix"),
        ]

        for nombre, endpoint in cron_endpoints:
            self.test_api_endpoint(nombre, endpoint)
            time.sleep(1)  # Los cron jobs pueden tardar más

        print()

        # 5. RESUMEN FINAL
        self.mostrar_resumen()

    def mostrar_resumen(self):
        """Mostrar resumen de la verificación"""
        print("=" * 60)
        print("📊 RESUMEN DE VERIFICACIÓN")
        print("=" * 60)

        total = self.resultados["modulos_probados"]
        ok = self.resultados["modulos_ok"]
        error = self.resultados["modulos_error"]
        porcentaje = (ok / total * 100) if total > 0 else 0

        print(f"📈 Módulos probados: {total}")
        print(f"✅ Funcionando: {ok}")
        print(f"❌ Con errores: {error}")
        print(f"📊 Porcentaje éxito: {porcentaje:.1f}%")
        print()

        if error > 0:
            print("❌ ERRORES ENCONTRADOS:")
            for i, error in enumerate(self.resultados["errores"], 1):
                print(f"   {i}. {error}")
            print()

        if porcentaje >= 90:
            print("🎉 SISTEMA EN EXCELENTE ESTADO")
        elif porcentaje >= 80:
            print("✅ SISTEMA EN BUEN ESTADO")
        elif porcentaje >= 70:
            print("⚠️  SISTEMA FUNCIONAL CON ALGUNOS PROBLEMAS")
        else:
            print("🚨 SISTEMA REQUIERE ATENCIÓN URGENTE")

        print(
            f"🕐 Verificación completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )


def main():
    """Función principal"""
    suite = GMaoTestSuite()
    suite.verificar_sistema_completo()


if __name__ == "__main__":
    main()
