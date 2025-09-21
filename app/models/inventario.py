from app.extensions import db


class Inventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(50))
    stock_actual = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=0)
    stock_maximo = db.Column(db.Integer, default=100)
    ubicacion = db.Column(db.String(50))
    precio_unitario = db.Column(db.Float)
    unidad_medida = db.Column(db.String(20))
    proveedor = db.Column(db.String(100))
    fecha_ultima_compra = db.Column(db.DateTime)
