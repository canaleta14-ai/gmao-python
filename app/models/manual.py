from app.extensions import db
from datetime import datetime


class Manual(db.Model):
    """Modelo para almacenar manuales de activos"""

    id = db.Column(db.Integer, primary_key=True)
    activo_id = db.Column(db.Integer, db.ForeignKey("activo.id"), nullable=False)
    nombre_archivo = db.Column(
        db.String(255), nullable=False
    )  # Nombre original del archivo
    nombre_unico = db.Column(
        db.String(255), nullable=False
    )  # Nombre único en el servidor
    tipo = db.Column(
        db.String(50), nullable=False
    )  # Tipo de manual (Manual de Usuario, etc.)
    descripcion = db.Column(db.Text)  # Descripción opcional
    ruta_archivo = db.Column(
        db.String(500), nullable=False
    )  # Ruta completa del archivo
    tamano = db.Column(db.Integer, nullable=False)  # Tamaño en bytes
    extension = db.Column(db.String(10), nullable=False)  # Extensión del archivo
    fecha_subida = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relación con activo
    activo = db.relationship(
        "Activo",
        backref=db.backref("manuales", lazy=True, cascade="all, delete-orphan"),
    )

    def __init__(
        self,
        activo_id,
        nombre_archivo,
        nombre_unico,
        tipo,
        descripcion,
        ruta_archivo,
        tamano,
        extension,
        fecha_subida=None,
    ):
        self.activo_id = activo_id
        self.nombre_archivo = nombre_archivo
        self.nombre_unico = nombre_unico
        self.tipo = tipo
        self.descripcion = descripcion
        self.ruta_archivo = ruta_archivo
        self.tamano = tamano
        self.extension = extension
        self.fecha_subida = fecha_subida or datetime.utcnow()

    def to_dict(self):
        """Convertir el manual a diccionario"""
        return {
            "id": self.id,
            "activo_id": self.activo_id,
            "nombre_archivo": self.nombre_archivo,
            "nombre_unico": self.nombre_unico,
            "tipo": self.tipo,
            "descripcion": self.descripcion,
            "ruta_archivo": self.ruta_archivo,
            "tamano": self.tamano,
            "extension": self.extension,
            "fecha_subida": (
                self.fecha_subida.isoformat() if self.fecha_subida else None
            ),
        }

    def __repr__(self):
        return f"<Manual {self.nombre_archivo} para Activo {self.activo_id}>"
