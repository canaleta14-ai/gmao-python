from flask_login import UserMixin
from app.extensions import db
from datetime import datetime


class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200))
    nombre = db.Column(db.String(100))
    rol = db.Column(db.String(50), default="TÃ©cnico")
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    ordenes = db.relationship("OrdenTrabajo", backref="tecnico", lazy=True)
