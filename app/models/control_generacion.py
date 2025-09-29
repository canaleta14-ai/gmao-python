"""
Modelo para control de generación de órdenes
"""

from app.extensions import db
from datetime import datetime


class ControlGeneracion(db.Model):
    """Control de generación diaria de órdenes para evitar duplicados"""

    __tablename__ = "control_generacion"

    id = db.Column(db.Integer, primary_key=True)
    fecha_generacion = db.Column(db.Date, nullable=False, unique=True, index=True)
    tipo_generacion = db.Column(
        db.String(20), nullable=False
    )  # 'manual' o 'automatico'
    timestamp_generacion = db.Column(db.DateTime, nullable=False, default=datetime.now)
    ordenes_generadas = db.Column(db.Integer, default=0)
    usuario_manual = db.Column(db.String(100))  # Si fue manual, quién lo hizo
    detalles = db.Column(db.Text)  # JSON con detalles adicionales

    def __repr__(self):
        return f"<ControlGeneracion {self.fecha_generacion} - {self.tipo_generacion}>"

    @staticmethod
    def ya_generado_hoy():
        """Verificar si ya se generaron órdenes para hoy"""
        from datetime import date

        hoy = date.today()
        return (
            ControlGeneracion.query.filter_by(fecha_generacion=hoy).first() is not None
        )

    @staticmethod
    def obtener_generacion_hoy():
        """Obtener el registro de generación de hoy si existe"""
        from datetime import date

        hoy = date.today()
        return ControlGeneracion.query.filter_by(fecha_generacion=hoy).first()

    @staticmethod
    def registrar_generacion(tipo, ordenes_count, usuario=None, detalles=None):
        """Registrar una nueva generación"""
        from datetime import date
        import json

        hoy = date.today()

        # Verificar si ya existe
        existente = ControlGeneracion.query.filter_by(fecha_generacion=hoy).first()
        if existente:
            return existente, False  # Ya existe, no se creó nuevo

        # Crear nuevo registro
        nuevo = ControlGeneracion(
            fecha_generacion=hoy,
            tipo_generacion=tipo,
            ordenes_generadas=ordenes_count,
            usuario_manual=usuario,
            detalles=json.dumps(detalles) if detalles else None,
        )

        db.session.add(nuevo)
        db.session.commit()

        return nuevo, True  # Creado exitosamente
