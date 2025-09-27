from app.extensions import db
from datetime import datetime, timezone


class OrdenRecambio(db.Model):
    """Modelo para gestionar recambios utilizados en órdenes de trabajo"""

    __tablename__ = "orden_recambio"

    id = db.Column(db.Integer, primary_key=True)
    orden_trabajo_id = db.Column(
        db.Integer, db.ForeignKey("orden_trabajo.id"), nullable=False
    )
    inventario_id = db.Column(
        db.Integer, db.ForeignKey("inventario.id"), nullable=False
    )
    cantidad_solicitada = db.Column(db.Integer, nullable=False)
    cantidad_utilizada = db.Column(db.Integer, default=0)
    precio_unitario = db.Column(db.Float)
    observaciones = db.Column(db.Text)
    fecha_asignacion = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    fecha_descuento = db.Column(db.DateTime)  # Cuando se descontó del stock
    descontado = db.Column(db.Boolean, default=False)

    # Relaciones
    orden_trabajo = db.relationship("OrdenTrabajo", backref="recambios")
    inventario = db.relationship("Inventario", backref="ordenes_recambios")

    def __repr__(self):
        return f'<OrdenRecambio {self.id}: {self.cantidad_utilizada}x {self.inventario.codigo if self.inventario else "N/A"}>'

    def to_dict(self):
        return {
            "id": self.id,
            "orden_trabajo_id": self.orden_trabajo_id,
            "inventario_id": self.inventario_id,
            "cantidad_solicitada": self.cantidad_solicitada,
            "cantidad_utilizada": self.cantidad_utilizada,
            "precio_unitario": self.precio_unitario,
            "observaciones": self.observaciones,
            "fecha_asignacion": (
                self.fecha_asignacion.isoformat() if self.fecha_asignacion else None
            ),
            "fecha_descuento": (
                self.fecha_descuento.isoformat() if self.fecha_descuento else None
            ),
            "descontado": self.descontado,
            "articulo": (
                {
                    "id": self.inventario.id,
                    "codigo": self.inventario.codigo,
                    "descripcion": self.inventario.descripcion,
                    "stock_actual": self.inventario.stock_actual,
                    "precio_promedio": self.inventario.precio_promedio,
                }
                if self.inventario
                else None
            ),
        }
