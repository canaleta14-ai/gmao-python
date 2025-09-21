from app.extensions import db
from datetime import datetime


class PlanMantenimiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo_plan = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    frecuencia = db.Column(db.String(50))
    frecuencia_dias = db.Column(db.Integer)
    ultima_ejecucion = db.Column(db.DateTime)
    proxima_ejecucion = db.Column(db.DateTime)
    estado = db.Column(db.String(50), default="Activo")
    descripcion = db.Column(db.Text)
    instrucciones = db.Column(db.Text)
    tiempo_estimado = db.Column(db.Float)

    activo_id = db.Column(db.Integer, db.ForeignKey("activo.id"))
