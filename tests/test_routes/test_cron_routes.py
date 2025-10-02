"""
Tests para endpoints de cron (Fase 5: Cloud Scheduler)
"""

import pytest
from datetime import datetime, timedelta


@pytest.mark.cron
class TestCronRoutes:

    def test_generar_ordenes_preventivas_desarrollo(
        self, client, plan_mantenimiento_test, app
    ):
        """Test generación de órdenes en modo desarrollo"""
        with app.app_context():
            response = client.post("/api/cron/generar-ordenes-preventivas")

            assert response.status_code == 200
            data = response.get_json()
            assert "planes_revisados" in data
            assert "ordenes_creadas" in data
            assert data["planes_revisados"] >= 1
            assert data["ordenes_creadas"] >= 1  # Al menos el plan de prueba

    def test_generar_ordenes_seguridad_produccion(
        self, client, app, plan_mantenimiento_test
    ):
        """Test seguridad en modo producción"""
        # Cambiar a modo producción
        app.config["FLASK_ENV"] = "production"

        with app.app_context():
            # Sin header - debe fallar
            response = client.post("/api/cron/generar-ordenes-preventivas")
            assert response.status_code == 403
            data = response.get_json()
            assert "error" in data

            # Con header incorrecto - debe fallar
            response = client.post(
                "/api/cron/generar-ordenes-preventivas",
                headers={"X-Appengine-Cron": "false"},
            )
            assert response.status_code == 403

            # Con header correcto - debe funcionar
            response = client.post(
                "/api/cron/generar-ordenes-preventivas",
                headers={"X-Appengine-Cron": "true"},
            )
            assert response.status_code == 200
            data = response.get_json()
            assert "ordenes_creadas" in data

        # Restaurar modo desarrollo
        app.config["FLASK_ENV"] = "development"

    def test_verificar_alertas(self, client, activo_test, app):
        """Test verificación de alertas de mantenimiento"""
        with app.app_context():
            response = client.post("/api/cron/verificar-alertas")

            assert response.status_code == 200
            data = response.get_json()
            assert "activos_revisados" in data
            assert "alertas_enviadas" in data
            assert data["activos_revisados"] >= 1

    def test_endpoint_test_cron(self, client, app):
        """Test endpoint de testing"""
        with app.app_context():
            response = client.get("/api/cron/test")

            assert response.status_code == 200
            data = response.get_json()
            assert "mensaje" in data
            assert "timestamp" in data
            assert data["mensaje"] == "Endpoint de cron funcionando"

    def test_crear_orden_actualiza_plan(
        self, client, plan_mantenimiento_test, app, db_session
    ):
        """Test que crear orden actualiza fechas del plan"""
        from app.models.plan_mantenimiento import PlanMantenimiento

        with app.app_context():
            # Obtener fecha inicial
            plan = (
                db_session.query(PlanMantenimiento)
                .filter_by(id=plan_mantenimiento_test.id)
                .first()
            )
            fecha_inicial = plan.proxima_ejecucion

            # Generar órdenes
            response = client.post("/api/cron/generar-ordenes-preventivas")
            assert response.status_code == 200

            # Verificar que se actualizó la próxima ejecución
            db_session.refresh(plan)
            assert plan.ultima_ejecucion is not None
            assert plan.proxima_ejecucion > fecha_inicial

    def test_generar_multiples_ordenes(
        self, client, app, db_session, activo_test, usuario_tecnico
    ):
        """Test generación de múltiples órdenes desde varios planes"""
        from app.models.plan_mantenimiento import PlanMantenimiento
        from datetime import datetime, timedelta

        with app.app_context():
            # Crear varios planes vencidos
            planes = []
            for i in range(3):
                plan = PlanMantenimiento(
                    nombre=f"Plan Test {i+1}",
                    descripcion=f"Descripción plan {i+1}",
                    tipo_mantenimiento="Preventivo",
                    activo_id=activo_test.id,
                    responsable_id=usuario_tecnico.id,
                    frecuencia="Mensual",
                    frecuencia_dias=30,
                    proxima_ejecucion=datetime.utcnow().date() - timedelta(days=i + 1),
                    activo=True,
                    duracion_estimada=2.0,
                )
                db_session.add(plan)
                planes.append(plan)
            db_session.commit()

            # Generar órdenes
            response = client.post("/api/cron/generar-ordenes-preventivas")
            assert response.status_code == 200

            data = response.get_json()
            # Debe haber revisado al menos 3 planes
            assert data["planes_revisados"] >= 3
            assert data["ordenes_creadas"] >= 3

    def test_verificar_alertas_seguridad(self, client, app):
        """Test seguridad de endpoint de alertas"""
        app.config["FLASK_ENV"] = "production"

        with app.app_context():
            # Sin header - debe fallar
            response = client.post("/api/cron/verificar-alertas")
            assert response.status_code == 403

            # Con header correcto - debe funcionar
            response = client.post(
                "/api/cron/verificar-alertas", headers={"X-Appengine-Cron": "true"}
            )
            assert response.status_code == 200

        app.config["FLASK_ENV"] = "development"

    def test_test_cron_solo_desarrollo(self, client, app):
        """Test que /test solo funciona en desarrollo"""
        # En desarrollo - debe funcionar
        response = client.get("/api/cron/test")
        assert response.status_code == 200

        # Cambiar a producción
        app.config["FLASK_ENV"] = "production"
        response = client.get("/api/cron/test")
        assert response.status_code == 403

        # Restaurar
        app.config["FLASK_ENV"] = "development"
