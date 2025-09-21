from app.extensions import db


class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    nif = db.Column(db.String(20), unique=True, nullable=False)
    cuenta_contable = db.Column(db.String(30), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(30))
    email = db.Column(db.String(120))
    contacto = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Proveedor {self.nombre} ({self.nif})>"
