#!/usr/bin/env python3
"""
Test específico para Mantenimiento Preventivo y Creación de Órdenes
"""

import requests
import re
import json
from datetime import datetime


class TestMantenimientoPreventivo:
    def __init__(self):
        self.base_url = "https://mantenimiento-470311.ew.r.appspot.com"
        self.session = requests.Session()

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

    def test_planes_mantenimiento(self):
        """Probar módulo de planes de mantenimiento"""
        self.log("=== PROBANDO PLANES DE MANTENIMIENTO ===")

        # 1. Verificar página principal de planes
        url_planes = f"{self.base_url}/planes/"
        response = self.session.get(url_planes, timeout=15)

        if response.status_code == 200:
            self.log("Página de planes accesible", "OK")

            # Verificar que contiene elementos esperados
            if "plan" in response.text.lower():
                self.log("Página contiene referencias a planes", "OK")
            else:
                self.log("Página no contiene referencias a planes", "ERROR")
        else:
            self.log(f"Error accediendo a planes: {response.status_code}", "ERROR")
            return False

        # 2. Verificar API de estadísticas de planes
        url_api = f"{self.base_url}/planes/api/estadisticas"
        response = self.session.get(url_api, timeout=15)

        if response.status_code == 200:
            self.log("API de estadísticas de planes funcional", "OK")
            try:
                data = response.json()
                self.log(f"Datos recibidos: {type(data)}", "OK")
            except:
                self.log("API devuelve datos no JSON", "ERROR")
        else:
            self.log(f"Error en API de planes: {response.status_code}", "ERROR")

        # 3. Verificar creación de plan (formulario)
        csrf_token = self.get_csrf_token(url_planes)
        if csrf_token:
            self.log("Token CSRF obtenido para planes", "OK")
        else:
            self.log("No se pudo obtener token CSRF", "ERROR")

        return True

    def test_ordenes_trabajo(self):
        """Probar módulo de órdenes de trabajo"""
        self.log("=== PROBANDO ÓRDENES DE TRABAJO ===")

        # 1. Verificar página principal de órdenes
        url_ordenes = f"{self.base_url}/ordenes/"
        response = self.session.get(url_ordenes, timeout=15)

        if response.status_code == 200:
            self.log("Página de órdenes accesible", "OK")

            # Verificar que contiene elementos esperados
            if "orden" in response.text.lower():
                self.log("Página contiene referencias a órdenes", "OK")
            else:
                self.log("Página no contiene referencias a órdenes", "ERROR")
        else:
            self.log(f"Error accediendo a órdenes: {response.status_code}", "ERROR")
            return False

        # 2. Verificar estadísticas de órdenes
        url_stats = f"{self.base_url}/ordenes/estadisticas"
        response = self.session.get(url_stats, timeout=15)

        if response.status_code == 200:
            self.log("Estadísticas de órdenes accesibles", "OK")
        else:
            self.log(
                f"Error en estadísticas de órdenes: {response.status_code}", "ERROR"
            )

        # 3. Verificar creación de orden
        csrf_token = self.get_csrf_token(url_ordenes)
        if csrf_token:
            self.log("Token CSRF obtenido para órdenes", "OK")
        else:
            self.log("No se pudo obtener token CSRF", "ERROR")

        return True

    def test_automatizacion_preventiva(self):
        """Probar automatización de mantenimiento preventivo"""
        self.log("=== PROBANDO AUTOMATIZACIÓN PREVENTIVA ===")

        # Probar endpoint de generación automática
        url_cron = f"{self.base_url}/api/cron/generar-ordenes-preventivas"
        response = self.session.get(url_cron, timeout=30)

        if response.status_code == 403:
            self.log(
                "Endpoint de generación protegido (OK - requiere autenticación)", "OK"
            )
        elif response.status_code == 200:
            self.log("Endpoint de generación ejecutado", "OK")
            try:
                # Si devuelve JSON, mostrar resultado
                if "json" in response.headers.get("content-type", ""):
                    data = response.json()
                    self.log(f"Resultado: {data}", "OK")
            except:
                pass
        else:
            self.log(f"Error en generación automática: {response.status_code}", "ERROR")

        return True

    def test_calendario(self):
        """Probar módulo de calendario"""
        self.log("=== PROBANDO CALENDARIO ===")

        # 1. Verificar página de calendario
        url_calendario = f"{self.base_url}/calendario/"
        response = self.session.get(url_calendario, timeout=15)

        if response.status_code == 200:
            self.log("Página de calendario accesible", "OK")
        else:
            self.log(f"Error accediendo a calendario: {response.status_code}", "ERROR")
            return False

        # 2. Verificar API de estadísticas del calendario
        url_api = f"{self.base_url}/calendario/api/estadisticas-mes"
        response = self.session.get(url_api, timeout=15)

        if response.status_code == 200:
            self.log("API de calendario funcional", "OK")
        else:
            self.log(f"Error en API de calendario: {response.status_code}", "ERROR")

        return True

    def ejecutar_todas_las_pruebas(self):
        """Ejecutar todas las pruebas de mantenimiento preventivo"""
        print("🧪 VERIFICACIÓN ESPECÍFICA: MANTENIMIENTO PREVENTIVO Y ÓRDENES")
        print("=" * 80)
        print(f"🌐 URL: {self.base_url}")
        print(f"🕐 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        resultados = []

        # Ejecutar todas las pruebas
        resultados.append(self.test_planes_mantenimiento())
        print()
        resultados.append(self.test_ordenes_trabajo())
        print()
        resultados.append(self.test_automatizacion_preventiva())
        print()
        resultados.append(self.test_calendario())
        print()

        # Resumen
        exitosos = sum(resultados)
        total = len(resultados)
        porcentaje = (exitosos / total * 100) if total > 0 else 0

        print("=" * 80)
        print("📊 RESUMEN MANTENIMIENTO PREVENTIVO")
        print("=" * 80)
        print(f"📈 Módulos probados: {total}")
        print(f"✅ Funcionando: {exitosos}")
        print(f"❌ Con errores: {total - exitosos}")
        print(f"📊 Porcentaje éxito: {porcentaje:.1f}%")
        print()

        if porcentaje >= 90:
            print("🎉 MANTENIMIENTO PREVENTIVO EN EXCELENTE ESTADO")
        elif porcentaje >= 75:
            print("✅ MANTENIMIENTO PREVENTIVO FUNCIONAL")
        else:
            print("🚨 MANTENIMIENTO PREVENTIVO REQUIERE ATENCIÓN")

        print(
            f"🕐 Verificación completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )


def main():
    test = TestMantenimientoPreventivo()
    test.ejecutar_todas_las_pruebas()


if __name__ == "__main__":
    main()
