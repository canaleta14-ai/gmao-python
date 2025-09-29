from app.extensions import db
from datetime import datetime, timezone


class SolicitudServicio(db.Model):
    __tablename__ = "solicitud_servicio"

    id = db.Column(db.Integer, primary_key=True)
    numero_solicitud = db.Column(db.String(50), unique=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_actualizacion = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Información del solicitante
    nombre_solicitante = db.Column(db.String(100), nullable=False)
    email_solicitante = db.Column(db.String(120), nullable=False)
    telefono_solicitante = db.Column(db.String(20))
    empresa_solicitante = db.Column(db.String(100))

    # Información del servicio solicitado
    tipo_servicio = db.Column(
        db.String(50), nullable=False
    )  # 'mantenimiento', 'reparacion', 'instalacion', 'otro'
    prioridad = db.Column(
        db.String(20), default="normal"
    )  # 'baja', 'normal', 'alta', 'urgente'
    estado = db.Column(
        db.String(50), default="pendiente"
    )  # 'pendiente', 'en_revision', 'aprobada', 'rechazada', 'en_progreso', 'completada', 'cancelada'

    # Detalles del servicio
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    ubicacion = db.Column(db.String(200))
    activo_afectado = db.Column(db.String(100))

    # Información adicional
    costo_estimado = db.Column(db.Float)
    tiempo_estimado = db.Column(db.String(50))  # ej: "2 horas", "1 día", etc.
    observaciones_internas = db.Column(db.Text)

    # Relaciones
    activo_id = db.Column(db.Integer, db.ForeignKey("activo.id"), nullable=True)
    asignado_a_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)

    # Relaciones con objetos
    activo = db.relationship("Activo", backref="solicitudes_servicio", lazy=True)
    asignado_a = db.relationship("Usuario", backref="solicitudes_asignadas", lazy=True)

    def __repr__(self):
        return f"<SolicitudServicio {self.numero_solicitud}: {self.titulo}>"

    @property
    def estado_display(self):
        """Retorna el nombre legible del estado"""
        estados = {
            "pendiente": "Pendiente",
            "en_revision": "En Revisión",
            "aprobada": "Aprobada",
            "rechazada": "Rechazada",
            "en_progreso": "En Progreso",
            "completada": "Completada",
            "cancelada": "Cancelada",
        }
        return estados.get(self.estado, self.estado)

    @property
    def prioridad_display(self):
        """Retorna el nombre legible de la prioridad"""
        prioridades = {
            "baja": "Baja",
            "normal": "Normal",
            "alta": "Alta",
            "urgente": "Urgente",
        }
        return prioridades.get(self.prioridad, self.prioridad)

    @property
    def tipo_servicio_display(self):
        """Retorna el nombre legible del tipo de servicio"""
        tipos = {
            "mantenimiento": "Mantenimiento",
            "reparacion": "Reparación",
            "instalacion": "Instalación",
            "otro": "Otro",
        }
        return tipos.get(self.tipo_servicio, self.tipo_servicio)
