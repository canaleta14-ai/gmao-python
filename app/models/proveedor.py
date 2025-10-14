from app.extensions import db


class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    nif = db.Column(db.String(20), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)
    contacto = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    cuenta_contable = db.Column(db.String(50), nullable=True)
    estado = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f"<Proveedor {self.nombre} ({self.nif})>"
