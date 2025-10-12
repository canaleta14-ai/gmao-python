"""
Blueprint de Alertas Inteligente
API REST para gestión del sistema de alertas
"""

from flask import Blueprint, request, jsonify, render_template
from flask_restx import Api, Resource, fields, Namespace
from app.models.alertas import (
    AlertaConfiguracion,
    AlertaHistorial,
    NotificacionLog,
    AlertaKPI,
)
from app.services.alert_engine import alert_engine
from app.services.notification_service import notification_service
from app.extensions import db, limiter
import json
from datetime import datetime, date
import pytz

# Crear blueprint
alertas_bp = Blueprint("alertas", __name__, url_prefix="/alertas")

# Configurar Flask-RESTX
alertas_api = Api(
    alertas_bp,
    version="1.0",
    title="Sistema de Alertas Inteligente",
    description="API para gestión de alertas automáticas del sistema GMAO",
    doc="/docs/",
    prefix="/api",
)

# Namespaces
configuracion_ns = alertas_api.namespace(
    "configuracion", description="Configuración de reglas de alertas"
)
historial_ns = alertas_api.namespace(
    "historial", description="Historial y gestión de alertas"
)
notificaciones_ns = alertas_api.namespace(
    "notificaciones", description="Gestión de notificaciones"
)
kpis_ns = alertas_api.namespace("kpis", description="KPIs y métricas del sistema")

# Modelos para documentación
alerta_config_model = alertas_api.model(
    "AlertaConfiguracion",
    {
        "id": fields.Integer(description="ID de la configuración"),
        "nombre": fields.String(required=True, description="Nombre de la alerta"),
        "descripcion": fields.String(description="Descripción detallada"),
        "tipo_alerta": fields.String(
            required=True,
            description="Tipo: stock, mantenimiento, equipos, performance",
        ),
        "prioridad": fields.String(
            required=True, description="Prioridad: critica, alta, media, baja"
        ),
        "condicion_sql": fields.String(
            required=True, description="Query SQL para evaluar condición"
        ),
        "umbral_valor": fields.Float(description="Valor umbral opcional"),
        "frecuencia_minutos": fields.Integer(
            description="Frecuencia de verificación en minutos"
        ),
        "activa": fields.Boolean(description="Si la alerta está activa"),
        "destinatarios_json": fields.String(description="JSON con destinatarios"),
        "escalamiento_json": fields.String(
            description="JSON con configuración de escalamiento"
        ),
    },
)

alerta_historial_model = alertas_api.model(
    "AlertaHistorial",
    {
        "id": fields.Integer(description="ID de la alerta"),
        "configuracion_id": fields.Integer(description="ID de la configuración"),
        "estado": fields.String(description="Estado: activa, reconocida, resuelta"),
        "mensaje": fields.String(description="Mensaje de la alerta"),
        "prioridad": fields.String(description="Prioridad de la alerta"),
        "fecha_deteccion": fields.DateTime(description="Fecha de detección"),
        "fecha_reconocimiento": fields.DateTime(description="Fecha de reconocimiento"),
        "fecha_resolucion": fields.DateTime(description="Fecha de resolución"),
        "usuario_asignado_id": fields.Integer(description="ID del usuario asignado"),
        "nivel_escalamiento": fields.Integer(description="Nivel de escalamiento"),
        "notas_resolucion": fields.String(description="Notas de resolución"),
    },
)

# =============================================================================
# CONFIGURACIÓN DE ALERTAS
# =============================================================================


@configuracion_ns.route("/")
class ConfiguracionList(Resource):
    @configuracion_ns.marshal_list_with(alerta_config_model)
    def get(self):
        """Obtener todas las configuraciones de alertas"""
        configuraciones = AlertaConfiguracion.query.all()
        return [config.to_dict() for config in configuraciones]

    @configuracion_ns.expect(alerta_config_model)
    @configuracion_ns.marshal_with(alerta_config_model)
    def post(self):
        """Crear nueva configuración de alerta"""
        try:
            data = request.get_json()

            # Validaciones
            if not data.get("nombre"):
                return {"error": "El nombre es requerido"}, 400
            if not data.get("condicion_sql"):
                return {"error": "La condición SQL es requerida"}, 400

            # Verificar que el nombre sea único
            if AlertaConfiguracion.query.filter_by(nombre=data["nombre"]).first():
                return {"error": "Ya existe una configuración con ese nombre"}, 400

            # Crear configuración
            configuracion = AlertaConfiguracion(
                nombre=data["nombre"],
                descripcion=data.get("descripcion", ""),
                tipo_alerta=data.get("tipo_alerta", "general"),
                prioridad=data.get("prioridad", "media"),
                condicion_sql=data["condicion_sql"],
                umbral_valor=data.get("umbral_valor"),
                frecuencia_minutos=data.get("frecuencia_minutos", 60),
                activa=data.get("activa", True),
                destinatarios_json=data.get("destinatarios_json"),
                escalamiento_json=data.get("escalamiento_json"),
            )

            db.session.add(configuracion)
            db.session.commit()

            return configuracion.to_dict(), 201

        except Exception as e:
            db.session.rollback()
            return {"error": f"Error creando configuración: {str(e)}"}, 500


@configuracion_ns.route("/<int:config_id>")
class ConfiguracionDetail(Resource):
    @configuracion_ns.marshal_with(alerta_config_model)
    def get(self, config_id):
        """Obtener configuración específica"""
        configuracion = AlertaConfiguracion.query.get_or_404(config_id)
        return configuracion.to_dict()

    @configuracion_ns.expect(alerta_config_model)
    @configuracion_ns.marshal_with(alerta_config_model)
    def put(self, config_id):
        """Actualizar configuración de alerta"""
        try:
            configuracion = AlertaConfiguracion.query.get_or_404(config_id)
            data = request.get_json()

            # Actualizar campos
            for campo in [
                "nombre",
                "descripcion",
                "tipo_alerta",
                "prioridad",
                "condicion_sql",
                "umbral_valor",
                "frecuencia_minutos",
                "activa",
                "destinatarios_json",
                "escalamiento_json",
            ]:
                if campo in data:
                    setattr(configuracion, campo, data[campo])

            db.session.commit()
            return configuracion.to_dict()

        except Exception as e:
            db.session.rollback()
            return {"error": f"Error actualizando configuración: {str(e)}"}, 500

    def delete(self, config_id):
        """Eliminar configuración de alerta"""
        try:
            configuracion = AlertaConfiguracion.query.get_or_404(config_id)
            db.session.delete(configuracion)
            db.session.commit()
            return {"message": "Configuración eliminada exitosamente"}, 200

        except Exception as e:
            db.session.rollback()
            return {"error": f"Error eliminando configuración: {str(e)}"}, 500


@configuracion_ns.route("/<int:config_id>/test")
class ConfiguracionTest(Resource):
    def post(self, config_id):
        """Probar una configuración de alerta"""
        try:
            configuracion = AlertaConfiguracion.query.get_or_404(config_id)
            resultado = alert_engine.evaluar_regla(configuracion)
            return resultado

        except Exception as e:
            return {"error": f"Error probando configuración: {str(e)}"}, 500


# =============================================================================
# HISTORIAL DE ALERTAS
# =============================================================================


@historial_ns.route("/")
class HistorialList(Resource):
    @historial_ns.marshal_list_with(alerta_historial_model)
    def get(self):
        """Obtener historial de alertas con filtros"""
        # Parámetros de filtro
        estado = request.args.get("estado")
        prioridad = request.args.get("prioridad")
        tipo_alerta = request.args.get("tipo_alerta")
        limite = request.args.get("limite", 50, type=int)

        # Construir query
        query = AlertaHistorial.query

        if estado:
            query = query.filter(AlertaHistorial.estado == estado)
        if prioridad:
            query = query.filter(AlertaHistorial.prioridad == prioridad)
        if tipo_alerta:
            query = query.join(AlertaConfiguracion).filter(
                AlertaConfiguracion.tipo_alerta == tipo_alerta
            )

        # Ordenar por fecha de detección descendente
        alertas = (
            query.order_by(AlertaHistorial.fecha_deteccion.desc()).limit(limite).all()
        )

        return [alerta.to_dict() for alerta in alertas]


@historial_ns.route("/<int:alerta_id>")
class HistorialDetail(Resource):
    @historial_ns.marshal_with(alerta_historial_model)
    def get(self, alerta_id):
        """Obtener detalles de una alerta específica"""
        alerta = AlertaHistorial.query.get_or_404(alerta_id)
        return alerta.to_dict()


@historial_ns.route("/<int:alerta_id>/reconocer")
class AlertaReconocer(Resource):
    def post(self, alerta_id):
        """Reconocer una alerta"""
        try:
            data = request.get_json() or {}
            usuario_id = data.get("usuario_id", 1)  # Por ahora usuario por defecto
            notas = data.get("notas", "")

            alerta = AlertaHistorial.query.get_or_404(alerta_id)

            if alerta.estado != "activa":
                return {"error": "Solo se pueden reconocer alertas activas"}, 400

            alerta.reconocer(usuario_id, notas)

            return {
                "message": "Alerta reconocida exitosamente",
                "alerta": alerta.to_dict(),
            }

        except Exception as e:
            return {"error": f"Error reconociendo alerta: {str(e)}"}, 500


@historial_ns.route("/<int:alerta_id>/resolver")
class AlertaResolver(Resource):
    def post(self, alerta_id):
        """Resolver una alerta"""
        try:
            data = request.get_json() or {}
            usuario_id = data.get("usuario_id", 1)  # Por ahora usuario por defecto
            notas = data.get("notas", "Alerta resuelta manualmente")

            if not notas:
                return {"error": "Las notas de resolución son requeridas"}, 400

            alerta = AlertaHistorial.query.get_or_404(alerta_id)

            if alerta.estado == "resuelta":
                return {"error": "La alerta ya está resuelta"}, 400

            alerta.resolver(usuario_id, notas)

            return {
                "message": "Alerta resuelta exitosamente",
                "alerta": alerta.to_dict(),
            }

        except Exception as e:
            return {"error": f"Error resolviendo alerta: {str(e)}"}, 500


# =============================================================================
# PROCESAMIENTO Y MOTOR
# =============================================================================


@alertas_api.route("/motor/procesar")
class MotorProcesar(Resource):
    def post(self):
        """Ejecutar procesamiento manual de todas las reglas"""
        try:
            resultado = alert_engine.procesar_todas_las_reglas()
            return resultado

        except Exception as e:
            return {"error": f"Error procesando reglas: {str(e)}"}, 500


@alertas_api.route("/motor/escalamiento")
class MotorEscalamiento(Resource):
    def post(self):
        """Verificar y procesar escalamientos pendientes"""
        try:
            alert_engine.verificar_escalamiento()
            return {"message": "Verificación de escalamiento completada"}

        except Exception as e:
            return {"error": f"Error procesando escalamiento: {str(e)}"}, 500


# =============================================================================
# KPIs Y MÉTRICAS
# =============================================================================


@kpis_ns.route("/dashboard")
class KPIDashboard(Resource):
    def get(self):
        """Obtener métricas para dashboard de KPIs"""
        try:
            hoy = date.today()

            # Métricas básicas
            total_alertas_activas = AlertaHistorial.query.filter_by(
                estado="activa"
            ).count()
            total_alertas_hoy = AlertaHistorial.query.filter(
                AlertaHistorial.fecha_deteccion >= hoy
            ).count()

            alertas_por_prioridad = {
                "critica": AlertaHistorial.query.filter_by(
                    estado="activa", prioridad="critica"
                ).count(),
                "alta": AlertaHistorial.query.filter_by(
                    estado="activa", prioridad="alta"
                ).count(),
                "media": AlertaHistorial.query.filter_by(
                    estado="activa", prioridad="media"
                ).count(),
                "baja": AlertaHistorial.query.filter_by(
                    estado="activa", prioridad="baja"
                ).count(),
            }

            configuraciones_activas = AlertaConfiguracion.query.filter_by(
                activa=True
            ).count()

            # Configurar zona horaria de España (maneja automáticamente UTC+1/UTC+2)
            zona_madrid = pytz.timezone("Europe/Madrid")
            hora_madrid = datetime.now(zona_madrid)

            return {
                "alertas_activas": total_alertas_activas,
                "alertas_hoy": total_alertas_hoy,
                "alertas_por_prioridad": alertas_por_prioridad,
                "configuraciones_activas": configuraciones_activas,
                "ultima_actualizacion": hora_madrid.isoformat(),
            }

        except Exception as e:
            return {"error": f"Error obteniendo KPIs: {str(e)}"}, 500


# =============================================================================
# RUTAS WEB (Templates)
# =============================================================================


@alertas_bp.route("/")
def dashboard():
    """Dashboard principal de alertas"""
    return render_template("alertas/dashboard.html", section="alertas")


@alertas_bp.route("/configuracion")
def configuracion():
    """Página de configuración de alertas"""
    return render_template("alertas/configuracion.html")


@alertas_bp.route("/historial")
def historial():
    """Página de historial de alertas"""
    return render_template("alertas/historial.html")


# =============================================================================
# CONFIGURACIÓN DE RATE LIMITING
# =============================================================================

# Aplicar rate limiting a endpoints críticos
# limiter.limit("30 per minute")(configuracion_ns.post)
# limiter.limit("60 per minute")(historial_ns.get)
# limiter.limit("10 per minute")(MotorProcesar.post)
