"""
Sistema de Alertas Inteligente - Modelos
Modelos de base de datos para el sistema de alertas
"""

from datetime import datetime
from app.extensions import db
from sqlalchemy import Text, JSON, Numeric
from sqlalchemy.sql import func


class AlertaConfiguracion(db.Model):
    """Configuración de reglas de alertas"""

    __tablename__ = "alertas_configuracion"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False, unique=True)
    descripcion = db.Column(Text)
    tipo_alerta = db.Column(
        db.String(50), nullable=False
    )  # 'stock', 'mantenimiento', 'equipos', 'performance'
    prioridad = db.Column(
        db.String(20), nullable=False
    )  # 'critica', 'alta', 'media', 'baja'
    condicion_sql = db.Column(
        Text, nullable=False
    )  # Query SQL para evaluar la condición
    umbral_valor = db.Column(Numeric(10, 2))  # Valor umbral opcional
    frecuencia_minutos = db.Column(db.Integer, default=60)  # Frecuencia de verificación
    activa = db.Column(db.Boolean, default=True)  # Si la alerta está activa
    destinatarios_json = db.Column(Text)  # JSON con lista de destinatarios
    escalamiento_json = db.Column(Text)  # JSON con configuración de escalamiento

    # Timestamps
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    # Relaciones
    alertas_historial = db.relationship(
        "AlertaHistorial", back_populates="configuracion", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<AlertaConfiguracion {self.nombre}>"

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "tipo_alerta": self.tipo_alerta,
            "prioridad": self.prioridad,
            "condicion_sql": self.condicion_sql,
            "umbral_valor": float(self.umbral_valor) if self.umbral_valor else None,
            "frecuencia_minutos": self.frecuencia_minutos,
            "activa": self.activa,
            "destinatarios_json": self.destinatarios_json,
            "escalamiento_json": self.escalamiento_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AlertaHistorial(db.Model):
    """Historial de alertas generadas"""

    __tablename__ = "alertas_historial"

    id = db.Column(db.Integer, primary_key=True)
    configuracion_id = db.Column(
        db.Integer, db.ForeignKey("alertas_configuracion.id"), nullable=False
    )
    prioridad = db.Column(
        db.String(20), nullable=False
    )  # Prioridad heredada de configuración
    estado = db.Column(
        db.String(20), nullable=False, default="activa"
    )  # 'activa', 'reconocida', 'resuelta', 'cerrada'
    mensaje = db.Column(Text, nullable=False)  # Mensaje descriptivo de la alerta
    datos_contexto = db.Column(Text)  # Datos adicionales en texto
    valor_actual = db.Column(Numeric(15, 4))  # Valor actual que disparó la alerta
    umbral_violado = db.Column(Numeric(15, 4))  # Umbral que fue violado
    asignado_a_id = db.Column(
        db.Integer
    )  # Usuario asignado para resolver (sin FK por ahora)

    # Timestamps de ciclo de vida
    fecha_deteccion = db.Column(db.DateTime, default=func.now())
    fecha_reconocimiento = db.Column(db.DateTime)
    fecha_resolucion = db.Column(db.DateTime)
    notas_resolucion = db.Column(Text)

    # Relaciones
    configuracion = db.relationship(
        "AlertaConfiguracion", back_populates="alertas_historial"
    )
    # usuario_asignado = db.relationship("Usuario", foreign_keys=[usuario_asignado_id])  # Comentado por ahora
    notificaciones = db.relationship(
        "NotificacionLog", back_populates="alerta", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<AlertaHistorial {self.id}: {self.mensaje[:50]}>"

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id": self.id,
            "configuracion_id": self.configuracion_id,
            "configuracion_nombre": (
                self.configuracion.nombre if self.configuracion else None
            ),
            "estado": self.estado,
            "mensaje": self.mensaje,
            "datos_contexto": self.datos_contexto,
            "valor_actual": float(self.valor_actual) if self.valor_actual else None,
            "umbral_violado": (
                float(self.umbral_violado) if self.umbral_violado else None
            ),
            "prioridad": self.prioridad,
            "asignado_a_id": self.asignado_a_id,
            "fecha_deteccion": (
                self.fecha_deteccion.isoformat() if self.fecha_deteccion else None
            ),
            "fecha_reconocimiento": (
                self.fecha_reconocimiento.isoformat()
                if self.fecha_reconocimiento
                else None
            ),
            "fecha_resolucion": (
                self.fecha_resolucion.isoformat() if self.fecha_resolucion else None
            ),
            "notas_resolucion": self.notas_resolucion,
            "tiempo_activa_minutos": self._calcular_tiempo_activa(),
        }

    def _calcular_tiempo_activa(self):
        """Calcula el tiempo que la alerta ha estado activa en minutos"""
        if self.estado == "resuelta" and self.fecha_resolucion:
            fin = self.fecha_resolucion
        else:
            fin = datetime.utcnow()

        inicio = self.fecha_deteccion or datetime.utcnow()
        delta = fin - inicio
        return int(delta.total_seconds() / 60)

    def reconocer(self, usuario_id, notas=None):
        """Marca la alerta como reconocida"""
        self.estado = "reconocida"
        self.fecha_reconocimiento = datetime.utcnow()
        self.asignado_a_id = usuario_id
        if notas:
            self.notas_resolucion = notas
        db.session.commit()

    def resolver(self, usuario_id, notas):
        """Marca la alerta como resuelta"""
        self.estado = "resuelta"
        self.fecha_resolucion = datetime.utcnow()
        self.asignado_a_id = usuario_id
        self.notas_resolucion = notas
        db.session.commit()


class NotificacionLog(db.Model):
    """Log de notificaciones enviadas"""

    __tablename__ = "notificaciones_log"

    id = db.Column(db.Integer, primary_key=True)
    alerta_id = db.Column(
        db.Integer, db.ForeignKey("alertas_historial.id"), nullable=False
    )
    canal = db.Column(
        db.String(20), nullable=False
    )  # 'email', 'dashboard', 'api', 'sms'
    destinatario = db.Column(
        db.String(255), nullable=False
    )  # Email, user_id, webhook_url, etc.
    asunto = db.Column(db.String(255))
    mensaje = db.Column(Text)
    estado = db.Column(
        db.String(20), default="pendiente"
    )  # 'pendiente', 'enviado', 'error', 'rebotado'

    # Control de reintento
    intentos = db.Column(db.Integer, default=0)
    maximo_intentos = db.Column(db.Integer, default=3)
    ultimo_intento = db.Column(db.DateTime)
    fecha_envio = db.Column(db.DateTime)
    error_mensaje = db.Column(Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=func.now())

    # Relaciones
    alerta = db.relationship("AlertaHistorial", back_populates="notificaciones")

    def __repr__(self):
        return f"<NotificacionLog {self.id}: {self.canal} -> {self.destinatario}>"

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id": self.id,
            "alerta_id": self.alerta_id,
            "canal": self.canal,
            "destinatario": self.destinatario,
            "asunto": self.asunto,
            "mensaje": self.mensaje,
            "estado": self.estado,
            "intentos": self.intentos,
            "maximo_intentos": self.maximo_intentos,
            "ultimo_intento": (
                self.ultimo_intento.isoformat() if self.ultimo_intento else None
            ),
            "fecha_envio": self.fecha_envio.isoformat() if self.fecha_envio else None,
            "error_mensaje": self.error_mensaje,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def marcar_enviado(self):
        """Marca la notificación como enviada exitosamente"""
        self.estado = "enviado"
        self.fecha_envio = datetime.utcnow()
        db.session.commit()

    def marcar_error(self, error_msg):
        """Marca la notificación con error"""
        self.estado = "error"
        self.error_mensaje = error_msg
        self.intentos += 1
        self.ultimo_intento = datetime.utcnow()
        db.session.commit()


class AlertaKPI(db.Model):
    """KPIs y métricas del sistema de alertas"""

    __tablename__ = "alertas_kpis"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False, unique=True)

    # Métricas de alertas
    total_alertas = db.Column(db.Integer, default=0)
    alertas_criticas = db.Column(db.Integer, default=0)
    alertas_altas = db.Column(db.Integer, default=0)
    alertas_medias = db.Column(db.Integer, default=0)
    alertas_bajas = db.Column(db.Integer, default=0)

    # Métricas de respuesta
    tiempo_promedio_respuesta = db.Column(db.Integer)  # en minutos
    tiempo_promedio_resolucion = db.Column(db.Integer)  # en minutos
    porcentaje_resueltas = db.Column(Numeric(5, 2))
    alertas_escaladas = db.Column(db.Integer, default=0)

    # Métricas de notificaciones
    notificaciones_enviadas = db.Column(db.Integer, default=0)
    notificaciones_error = db.Column(db.Integer, default=0)
    tasa_entrega = db.Column(Numeric(5, 2))

    # Timestamps
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AlertaKPI {self.fecha}: {self.total_alertas} alertas>"

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "total_alertas": self.total_alertas,
            "alertas_criticas": self.alertas_criticas,
            "alertas_altas": self.alertas_altas,
            "alertas_medias": self.alertas_medias,
            "alertas_bajas": self.alertas_bajas,
            "tiempo_promedio_respuesta": self.tiempo_promedio_respuesta,
            "tiempo_promedio_resolucion": self.tiempo_promedio_resolucion,
            "porcentaje_resueltas": (
                float(self.porcentaje_resueltas) if self.porcentaje_resueltas else None
            ),
            "alertas_escaladas": self.alertas_escaladas,
            "notificaciones_enviadas": self.notificaciones_enviadas,
            "notificaciones_error": self.notificaciones_error,
            "tasa_entrega": float(self.tasa_entrega) if self.tasa_entrega else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
