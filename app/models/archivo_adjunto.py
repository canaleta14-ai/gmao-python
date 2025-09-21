from app.extensions import db
from datetime import datetime, timezone


class ArchivoAdjunto(db.Model):
    """Modelo para gestionar archivos adjuntos a las órdenes de trabajo"""

    __tablename__ = "archivo_adjunto"

    id = db.Column(db.Integer, primary_key=True)
    nombre_original = db.Column(db.String(255), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)  # Nombre único generado
    tipo_archivo = db.Column(db.String(50), nullable=False)  # imagen, documento, enlace
    extension = db.Column(db.String(10))
    tamaño = db.Column(db.Integer)  # En bytes
    ruta_archivo = db.Column(db.String(500))  # Ruta del archivo en el servidor
    url_enlace = db.Column(db.String(1000))  # Para enlaces externos
    descripcion = db.Column(db.Text)
    fecha_subida = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relación con orden de trabajo
    orden_trabajo_id = db.Column(
        db.Integer, db.ForeignKey("orden_trabajo.id"), nullable=False
    )

    # Usuario que subió el archivo
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))

    def __repr__(self):
        return f"<ArchivoAdjunto {self.nombre_original}>"

    def to_dict(self):
        """Convierte el objeto a diccionario para JSON"""
        return {
            "id": self.id,
            "nombre_original": self.nombre_original,
            "nombre_archivo": self.nombre_archivo,
            "tipo_archivo": self.tipo_archivo,
            "extension": self.extension,
            "tamaño": self.tamaño,
            "ruta_archivo": self.ruta_archivo,
            "url_enlace": self.url_enlace,
            "descripcion": self.descripcion,
            "fecha_subida": (
                self.fecha_subida.isoformat() if self.fecha_subida else None
            ),
            "orden_trabajo_id": self.orden_trabajo_id,
            "usuario_id": self.usuario_id,
        }

    @property
    def es_imagen(self):
        """Verifica si el archivo es una imagen"""
        extensiones_imagen = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
        return self.extension and self.extension.lower() in extensiones_imagen

    @property
    def es_documento(self):
        """Verifica si el archivo es un documento"""
        extensiones_documento = [
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".txt",
            ".csv",
        ]
        return self.extension and self.extension.lower() in extensiones_documento

    @property
    def es_enlace(self):
        """Verifica si es un enlace externo"""
        return self.tipo_archivo == "enlace"

    @property
    def tamaño_legible(self):
        """Convierte el tamaño en bytes a formato legible"""
        if not self.tamaño:
            return "0 B"

        for unidad in ["B", "KB", "MB", "GB"]:
            if self.tamaño < 1024.0:
                return f"{self.tamaño:.1f} {unidad}"
            self.tamaño /= 1024.0
        return f"{self.tamaño:.1f} TB"
