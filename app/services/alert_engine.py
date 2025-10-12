"""
Sistema de Alertas Inteligente - Motor de Alertas
Motor principal para evaluar reglas y generar alertas automáticamente
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from app.extensions import db
from app.models.alertas import AlertaConfiguracion, AlertaHistorial, NotificacionLog

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertEngine:
    """Motor principal de alertas"""

    def __init__(self):
        self.logger = logger
        self.active_alerts = {}  # Cache de alertas activas

    def procesar_todas_las_reglas(self) -> Dict[str, Any]:
        """Procesa todas las reglas de alertas activas"""
        resultado = {
            "procesadas": 0,
            "alertas_nuevas": 0,
            "alertas_resueltas": 0,
            "errores": [],
        }

        try:
            # Obtener todas las reglas activas
            reglas = AlertaConfiguracion.query.filter_by(activa=True).all()
            resultado["procesadas"] = len(reglas)

            for regla in reglas:
                try:
                    resultado_regla = self.evaluar_regla(regla)

                    if resultado_regla["alerta_activada"]:
                        resultado["alertas_nuevas"] += 1
                    elif resultado_regla["alerta_resuelta"]:
                        resultado["alertas_resueltas"] += 1

                except Exception as e:
                    error_msg = f"Error procesando regla {regla.nombre}: {str(e)}"
                    self.logger.error(error_msg)
                    resultado["errores"].append(error_msg)

            self.logger.info(f"Procesamiento completado: {resultado}")
            return resultado

        except Exception as e:
            error_msg = f"Error en procesar_todas_las_reglas: {str(e)}"
            self.logger.error(error_msg)
            resultado["errores"].append(error_msg)
            return resultado

    def evaluar_regla(self, regla: AlertaConfiguracion) -> Dict[str, Any]:
        """Evalúa una regla específica de alerta"""
        resultado = {
            "regla_id": regla.id,
            "regla_nombre": regla.nombre,
            "condicion_cumplida": False,
            "alerta_activada": False,
            "alerta_resuelta": False,
            "datos": None,
            "error": None,
        }

        try:
            # Ejecutar la consulta SQL de la condición
            datos = self.ejecutar_condicion_sql(regla.condicion_sql)
            resultado["datos"] = datos

            # Evaluar si la condición se cumple
            condicion_cumplida = self.evaluar_condicion(datos, regla.umbral_valor)
            resultado["condicion_cumplida"] = condicion_cumplida

            # Verificar si ya existe una alerta activa para esta regla
            alerta_existente = AlertaHistorial.query.filter_by(
                configuracion_id=regla.id, estado="activa"
            ).first()

            if condicion_cumplida and not alerta_existente:
                # Crear nueva alerta
                nueva_alerta = self.crear_alerta(regla, datos)
                resultado["alerta_activada"] = True
                resultado["alerta_id"] = nueva_alerta.id

                # Enviar notificaciones
                self.enviar_notificaciones(nueva_alerta)

            elif not condicion_cumplida and alerta_existente:
                # Resolver alerta existente automáticamente
                self.resolver_alerta_automatica(alerta_existente)
                resultado["alerta_resuelta"] = True
                resultado["alerta_id"] = alerta_existente.id

            return resultado

        except Exception as e:
            error_msg = f"Error evaluando regla {regla.nombre}: {str(e)}"
            self.logger.error(error_msg)
            resultado["error"] = error_msg
            return resultado

    def ejecutar_condicion_sql(self, condicion_sql: str) -> List[Dict]:
        """Ejecuta la consulta SQL de condición de manera segura"""
        try:
            # Validar que la consulta sea de solo lectura (SELECT)
            sql_limpio = condicion_sql.strip().upper()
            if not sql_limpio.startswith("SELECT"):
                raise ValueError("Solo se permiten consultas SELECT")

            # Palabras prohibidas para seguridad
            palabras_prohibidas = [
                "DELETE",
                "UPDATE",
                "INSERT",
                "DROP",
                "ALTER",
                "CREATE",
            ]
            for palabra in palabras_prohibidas:
                if palabra in sql_limpio:
                    raise ValueError(f"Palabra prohibida encontrada: {palabra}")

            # Ejecutar consulta
            result = db.session.execute(text(condicion_sql))

            # Convertir resultado a lista de diccionarios
            columnas = result.keys()
            filas = []
            for fila in result:
                fila_dict = {}
                for i, valor in enumerate(fila):
                    fila_dict[columnas[i]] = valor
                filas.append(fila_dict)

            return filas

        except Exception as e:
            self.logger.error(
                f"Error ejecutando SQL: {condicion_sql} - Error: {str(e)}"
            )
            raise e

    def evaluar_condicion(self, datos: List[Dict], umbral: Optional[float]) -> bool:
        """Evalúa si los datos cumplen la condición de alerta"""
        if not datos:
            return False

        # Si no hay umbral, cualquier resultado indica condición cumplida
        if umbral is None:
            return len(datos) > 0

        # Si hay umbral, verificar el primer valor numérico
        primera_fila = datos[0]
        for valor in primera_fila.values():
            if isinstance(valor, (int, float)):
                return valor >= umbral

        # Si no hay valores numéricos, evaluar por cantidad de registros
        return len(datos) >= umbral

    def crear_alerta(
        self, regla: AlertaConfiguracion, datos: List[Dict]
    ) -> AlertaHistorial:
        """Crea una nueva alerta"""
        try:
            # Generar mensaje descriptivo
            mensaje = self.generar_mensaje_alerta(regla, datos)

            # Crear alerta
            alerta = AlertaHistorial(
                configuracion_id=regla.id,
                estado="activa",
                mensaje=mensaje,
                datos_json=json.dumps(datos, default=str),
                prioridad=regla.prioridad,
                fecha_activacion=datetime.utcnow(),
                nivel_escalamiento=1,
                escalamiento_automatico=True,
            )

            db.session.add(alerta)
            db.session.commit()

            self.logger.info(f"Alerta creada: {alerta.id} - {mensaje}")
            return alerta

        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creando alerta: {str(e)}")
            raise e

    def generar_mensaje_alerta(
        self, regla: AlertaConfiguracion, datos: List[Dict]
    ) -> str:
        """Genera un mensaje descriptivo para la alerta"""
        base_msg = f"🚨 {regla.nombre}"

        if regla.tipo_alerta == "stock":
            if datos and "nombre" in datos[0] and "cantidad_actual" in datos[0]:
                item = datos[0]
                base_msg += f" - {item['nombre']}: {item['cantidad_actual']} unidades"

        elif regla.tipo_alerta == "mantenimiento":
            if datos and "equipo_nombre" in datos[0]:
                item = datos[0]
                base_msg += f" - Equipo: {item['equipo_nombre']}"

        elif regla.tipo_alerta == "equipos":
            if datos and "nombre" in datos[0]:
                item = datos[0]
                base_msg += f" - Equipo: {item['nombre']}"

        elif regla.tipo_alerta == "performance":
            if datos and len(datos) > 0:
                base_msg += f" - {len(datos)} elementos afectados"

        # Agregar nivel de prioridad
        if regla.prioridad == "critica":
            base_msg = f"🔴 CRÍTICO: {base_msg}"
        elif regla.prioridad == "alta":
            base_msg = f"🟡 ALTA: {base_msg}"
        elif regla.prioridad == "media":
            base_msg = f"🟠 MEDIA: {base_msg}"
        else:
            base_msg = f"🟢 BAJA: {base_msg}"

        return base_msg

    def resolver_alerta_automatica(self, alerta: AlertaHistorial):
        """Resuelve una alerta automáticamente cuando la condición ya no se cumple"""
        try:
            alerta.estado = "resuelta"
            alerta.fecha_resolucion = datetime.utcnow()
            alerta.notas_resolucion = (
                "Alerta resuelta automáticamente - condición ya no se cumple"
            )

            db.session.commit()

            self.logger.info(f"Alerta resuelta automáticamente: {alerta.id}")

            # Enviar notificación de resolución
            self.enviar_notificacion_resolucion(alerta)

        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error resolviendo alerta automática: {str(e)}")

    def enviar_notificaciones(self, alerta: AlertaHistorial):
        """Envía notificaciones para una nueva alerta"""
        try:
            from app.services.notification_service import NotificationService

            notification_service = NotificationService()

            # Obtener destinatarios de la configuración
            destinatarios = self.obtener_destinatarios(alerta.configuracion)

            for destinatario in destinatarios:
                # Crear registro de notificación
                notificacion = NotificacionLog(
                    alerta_id=alerta.id,
                    canal=destinatario["canal"],
                    destinatario=destinatario["direccion"],
                    asunto=f"Nueva Alerta: {alerta.configuracion.nombre}",
                    mensaje=alerta.mensaje,
                    estado="pendiente",
                )

                db.session.add(notificacion)
                db.session.commit()

                # Enviar notificación según el canal
                if destinatario["canal"] == "email":
                    notification_service.enviar_email_alerta(
                        alerta, destinatario["direccion"]
                    )
                elif destinatario["canal"] == "dashboard":
                    notification_service.enviar_notificacion_dashboard(
                        alerta, destinatario["direccion"]
                    )

        except Exception as e:
            self.logger.error(f"Error enviando notificaciones: {str(e)}")

    def enviar_notificacion_resolucion(self, alerta: AlertaHistorial):
        """Envía notificación de resolución de alerta"""
        try:
            from app.services.notification_service import NotificationService

            notification_service = NotificationService()
            destinatarios = self.obtener_destinatarios(alerta.configuracion)

            for destinatario in destinatarios:
                if destinatario["canal"] == "email":
                    notification_service.enviar_email_resolucion(
                        alerta, destinatario["direccion"]
                    )

        except Exception as e:
            self.logger.error(f"Error enviando notificación de resolución: {str(e)}")

    def obtener_destinatarios(self, configuracion: AlertaConfiguracion) -> List[Dict]:
        """Obtiene la lista de destinatarios desde la configuración JSON"""
        try:
            if not configuracion.destinatarios_json:
                return []

            destinatarios_data = json.loads(configuracion.destinatarios_json)

            # Formato esperado: [{"canal": "email", "direccion": "user@domain.com"}, ...]
            return destinatarios_data

        except Exception as e:
            self.logger.error(f"Error parseando destinatarios: {str(e)}")
            return []

    def verificar_escalamiento(self):
        """Verifica alertas que requieren escalamiento"""
        try:
            # Obtener alertas activas que puedan necesitar escalamiento
            alertas_activas = AlertaHistorial.query.filter_by(
                estado="activa", escalamiento_automatico=True
            ).all()

            for alerta in alertas_activas:
                if self.debe_escalar(alerta):
                    self.escalar_alerta(alerta)

        except Exception as e:
            self.logger.error(f"Error verificando escalamiento: {str(e)}")

    def debe_escalar(self, alerta: AlertaHistorial) -> bool:
        """Determina si una alerta debe escalarse"""
        # Configuración de escalamiento por prioridad (en minutos)
        tiempos_escalamiento = {
            "critica": [15, 30, 60],  # Escalar a los 15, 30 y 60 minutos
            "alta": [30, 60, 120],  # Escalar a los 30, 60 y 120 minutos
            "media": [60, 180, 360],  # Escalar a los 60, 180 y 360 minutos
            "baja": [180, 720, 1440],  # Escalar a los 180, 720 y 1440 minutos
        }

        tiempo_activa = alerta._calcular_tiempo_activa()
        tiempos = tiempos_escalamiento.get(alerta.prioridad, [60, 180, 360])

        # Verificar si es tiempo de escalar al siguiente nivel
        if alerta.nivel_escalamiento <= len(tiempos):
            tiempo_limite = tiempos[alerta.nivel_escalamiento - 1]
            return tiempo_activa >= tiempo_limite

        return False

    def escalar_alerta(self, alerta: AlertaHistorial):
        """Escala una alerta al siguiente nivel"""
        try:
            alerta.nivel_escalamiento += 1
            alerta.fecha_ultimo_escalamiento = datetime.utcnow()

            db.session.commit()

            self.logger.info(
                f"Alerta escalada: {alerta.id} - Nivel {alerta.nivel_escalamiento}"
            )

            # Enviar notificaciones de escalamiento
            self.enviar_notificaciones_escalamiento(alerta)

        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error escalando alerta: {str(e)}")

    def enviar_notificaciones_escalamiento(self, alerta: AlertaHistorial):
        """Envía notificaciones de escalamiento"""
        try:
            from app.services.notification_service import NotificationService

            notification_service = NotificationService()

            # Obtener destinatarios según el nivel de escalamiento
            destinatarios = self.obtener_destinatarios_escalamiento(alerta)

            for destinatario in destinatarios:
                notification_service.enviar_email_escalamiento(alerta, destinatario)

        except Exception as e:
            self.logger.error(
                f"Error enviando notificaciones de escalamiento: {str(e)}"
            )

    def obtener_destinatarios_escalamiento(self, alerta: AlertaHistorial) -> List[str]:
        """Obtiene destinatarios según el nivel de escalamiento"""
        # Esta lógica puede ser más compleja según las necesidades
        # Por ahora, usar los mismos destinatarios de la configuración
        destinatarios = self.obtener_destinatarios(alerta.configuracion)
        return [d["direccion"] for d in destinatarios if d["canal"] == "email"]


# Instancia global del motor de alertas
alert_engine = AlertEngine()
