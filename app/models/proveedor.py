from app.extensions import db

class Proveedor(db.Model):
    __tablename__ = "proveedor"
    id = db.Column(db.Integer, primary_key=True)
    proveedor = db.Column(db.String(255))         # Nombre del proveedor
    nif = db.Column(db.String(50))
    direccion = db.Column(db.String(255))
    contacto = db.Column(db.String(100))
    email = db.Column(db.String(120))
    cuenta_contable = db.Column(db.String(50))
    estado = db.Column(db.String(50))