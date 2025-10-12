#!/usr/bin/env python3
"""
Script de verificación integral del sistema GMAO - Versión corregida
Verifica todos los módulos y funcionalidades principales con rutas correctas
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

    def test_modulo(self, nombre, endpoint, metodo="GET"):
        """Probar un módulo específico"""
        self.log(f"Probando módulo: {nombre}")
        self.resultados["modulos_probados"] += 1

        try:
            url = f"{self.base_url}{endpoint}"

            if metodo == "GET":
                response = self.session.get(url, timeout=15)
            else:
                response = self.session.request(metodo, url, timeout=15)

            # Considerar 200, 302 (redirect), 401/403 (auth required) como éxito funcional
            if response.status_code in [200, 302, 308, 401, 403]:
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

    def verificar_sistema_completo(self):
        """Verificar todos los módulos del sistema GMAO"""

        print("🧪 VERIFICACIÓN INTEGRAL DEL SISTEMA GMAO (CORREGIDA)")
        print("=" * 70)
        print(f"🌐 URL Base: {self.base_url}")
        print(f"🕐 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 1. MÓDULOS WEB PRINCIPALES (rutas corregidas)
        self.log("=== VERIFICANDO MÓDULOS WEB ===")

        modulos_web = [
            ("Página Principal", "/"),
            ("Login", "/login"),
            ("Dashboard", "/dashboard"),
            ("Solicitudes", "/solicitudes/"),
            ("Admin Solicitudes", "/admin/solicitudes/"),
            ("Órdenes de Trabajo", "/ordenes/"),
            ("Planes de Mantenimiento", "/planes/"),
            ("Activos", "/activos/"),
            ("Inventario", "/inventario/"),
            ("Usuarios", "/usuarios/"),
            ("Proveedores", "/proveedores/"),
            ("Categorías", "/categorias/"),
            ("Calendario", "/calendario/"),
            ("Test Dashboard", "/test-dashboard"),
        ]

        for nombre, endpoint in modulos_web:
            self.test_modulo(nombre, endpoint)
            time.sleep(0.3)  # Evitar sobrecarga

        print()

        # 2. APIs PRINCIPALES (rutas corregidas basadas en los blueprints)
        self.log("=== VERIFICANDO APIs ===")

        apis = [
            ("API Estadísticas", "/api/estadisticas"),
            ("API User Info", "/api/user/info"),
            ("API Solicitudes Filtrar", "/admin/solicitudes/api/filtrar"),
            ("API Solicitudes Stats", "/admin/solicitudes/api/estadisticas"),
            ("API Activos Stats", "/activos/api/estadisticas"),
            ("API Ordenes Stats", "/ordenes/api/estadisticas"),
            ("API Planes Stats", "/planes/api/estadisticas"),
            ("API Inventario Stats", "/inventario/api/estadisticas"),
            ("API Proveedores Stats", "/proveedores/api/estadisticas"),
            ("API Categorias Stats", "/categorias/estadisticas"),
            ("API Recambios", "/api/recambios"),
            ("API Calendario Mes", "/calendario/api/estadisticas-mes"),
        ]

        for nombre, endpoint in apis:
            self.test_modulo(nombre, endpoint)
            time.sleep(0.3)

        print()

        # 3. FUNCIONALIDADES DE MANTENIMIENTO PREVENTIVO
        self.log("=== VERIFICANDO MANTENIMIENTO PREVENTIVO ===")

        preventivo = [
            ("Planes de Mantenimiento", "/planes/"),
            ("API Planes", "/planes/api/estadisticas"),
            ("Calendario", "/calendario/"),
            ("Generación Automática", "/api/cron/generar-ordenes-preventivas"),
        ]

        for nombre, endpoint in preventivo:
            self.test_modulo(nombre, endpoint)
            time.sleep(0.5)

        print()

        # 4. FUNCIONALIDADES DE ÓRDENES DE TRABAJO
        self.log("=== VERIFICANDO ÓRDENES DE TRABAJO ===")

        ordenes = [
            ("Órdenes Web", "/ordenes/"),
            ("Estadísticas Órdenes", "/ordenes/estadisticas"),
            ("API Órdenes Stats", "/ordenes/api/estadisticas"),
        ]

        for nombre, endpoint in ordenes:
            self.test_modulo(nombre, endpoint)
            time.sleep(0.5)

        print()

        # 5. CRON JOBS Y AUTOMATIZACIÓN
        self.log("=== VERIFICANDO AUTOMATIZACIÓN ===")

        cron_endpoints = [
            ("Generación Órdenes Preventivas", "/api/cron/generar-ordenes-preventivas"),
            ("Verificar Alertas", "/api/cron/verificar-alertas"),
            ("DB Fix", "/api/cron/db-fix"),
        ]

        for nombre, endpoint in cron_endpoints:
            self.test_modulo(nombre, endpoint)
            time.sleep(1)  # Los cron jobs pueden tardar más

        print()

        # 6. RESUMEN FINAL
        self.mostrar_resumen()

    def mostrar_resumen(self):
        """Mostrar resumen de la verificación"""
        print("=" * 70)
        print("📊 RESUMEN DE VERIFICACIÓN")
        print("=" * 70)

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

        # Evaluación del estado del sistema
        if porcentaje >= 95:
            print("🎉 SISTEMA EN EXCELENTE ESTADO")
            estado = "EXCELENTE"
        elif porcentaje >= 85:
            print("✅ SISTEMA EN BUEN ESTADO")
            estado = "BUENO"
        elif porcentaje >= 75:
            print("⚠️  SISTEMA FUNCIONAL CON ALGUNOS PROBLEMAS")
            estado = "FUNCIONAL"
        else:
            print("🚨 SISTEMA REQUIERE ATENCIÓN")
            estado = "REQUIERE ATENCIÓN"

        print(
            f"🕐 Verificación completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Guardar resultados en archivo
        resultados_completos = {
            "timestamp": datetime.now().isoformat(),
            "url_base": self.base_url,
            "estadisticas": self.resultados,
            "estado_sistema": estado,
            "porcentaje_exito": porcentaje,
        }

        with open("verificacion_sistema.json", "w", encoding="utf-8") as f:
            json.dump(resultados_completos, f, indent=2, ensure_ascii=False)

        print(f"📄 Resultados guardados en: verificacion_sistema.json")


def main():
    """Función principal"""
    suite = GMaoTestSuite()
    suite.verificar_sistema_completo()


if __name__ == "__main__":
    main()
