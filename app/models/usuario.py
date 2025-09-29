from flask_login import UserMixin
from app.extensions import db
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash


class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200))
    nombre = db.Column(db.String(100))
    rol = db.Column(db.String(50), default="Técnico")
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    ordenes = db.relationship("OrdenTrabajo", backref="tecnico", lazy=True)

    def check_password(self, password):
        """Verificar la contraseña"""
        return check_password_hash(self.password, password)

    def set_password(self, password):
        """Establecer la contraseña encriptada"""
        self.password = generate_password_hash(password)
