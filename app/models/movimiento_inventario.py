from app.extensions import db
from datetime import datetime, timezone


class MovimientoInventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    tipo = db.Column(db.String(20))
    cantidad = db.Column(db.Integer)
    precio = db.Column(db.Float)
    observaciones = db.Column(db.Text)

    inventario_id = db.Column(db.Integer, db.ForeignKey("inventario.id"))
    orden_trabajo_id = db.Column(
        db.Integer, db.ForeignKey("orden_trabajo.id"), nullable=True
    )
