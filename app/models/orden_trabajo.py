from app.extensions import db
from datetime import datetime, timezone


class OrdenTrabajo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_orden = db.Column(db.String(50), unique=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_programada = db.Column(db.DateTime)
    fecha_completada = db.Column(db.DateTime)
    tipo = db.Column(db.String(50))
    prioridad = db.Column(db.String(20))
    estado = db.Column(db.String(50), default="Pendiente")
    descripcion = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    tiempo_estimado = db.Column(db.Float)
    tiempo_real = db.Column(db.Float)

    activo_id = db.Column(db.Integer, db.ForeignKey("activo.id"))
    tecnico_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))

    # Relación con plan de mantenimiento (opcional, para órdenes generadas automáticamente)
    plan_mantenimiento_id = db.Column(
        db.Integer, db.ForeignKey("plan_mantenimiento.id"), nullable=True
    )

    # Nota: La relación 'activo' está definida en el modelo Activo con backref
    # Nota: La relación 'tecnico' está definida en el modelo Usuario con backref
    # Nota: La relación 'plan_mantenimiento' se define con backref aquí abajo

    # Relación con archivos adjuntos
    archivos_adjuntos = db.relationship(
        "ArchivoAdjunto",
        backref="orden_trabajo",
        lazy=True,
        cascade="all, delete-orphan",
    )

    # Relación con plan de mantenimiento
    plan_mantenimiento = db.relationship(
        "PlanMantenimiento", backref="ordenes_generadas", lazy=True
    )

    # Relación con recambios utilizados
    # Nota: La relación inversa está definida en OrdenRecambio.orden_trabajo
