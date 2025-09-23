from app.extensions import db
from datetime import datetime, timezone


class MovimientoInventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Tipos de movimiento
    tipo = db.Column(
        db.String(20)
    )  # entrada, salida, ajuste, regularizacion, transferencia
    subtipo = db.Column(
        db.String(30)
    )  # compra, consumo, devolucion, inventario_inicial, inventario_final, etc.

    # Cantidades
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float)
    valor_total = db.Column(db.Float)

    # Información contable
    cuenta_contable = db.Column(
        db.String(9)
    )  # Heredada del artículo pero puede ser específica
    centro_costo = db.Column(db.String(20))

    # Referencias
    documento_referencia = db.Column(db.String(50))  # Número de factura, orden, etc.
    observaciones = db.Column(db.Text)

    # Control
    usuario_id = db.Column(db.String(50))
    aprobado = db.Column(db.Boolean, default=False)
    fecha_aprobacion = db.Column(db.DateTime)
    usuario_aprobacion = db.Column(db.String(50))

    # Relaciones
    inventario_id = db.Column(
        db.Integer, db.ForeignKey("inventario.id"), nullable=False
    )
    orden_trabajo_id = db.Column(
        db.Integer, db.ForeignKey("orden_trabajo.id"), nullable=True
    )
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedor.id"), nullable=True)
    conteo_inventario_id = db.Column(
        db.Integer, db.ForeignKey("conteo_inventario.id"), nullable=True
    )

    def __repr__(self):
        return f"<MovimientoInventario {self.tipo} - {self.cantidad} - {self.fecha}>"

    @property
    def es_entrada(self):
        """Indica si el movimiento es una entrada de stock"""
        return self.tipo in ["entrada", "ajuste"] and self.cantidad > 0

    @property
    def es_salida(self):
        """Indica si el movimiento es una salida de stock"""
        return self.tipo in ["salida", "ajuste"] and self.cantidad < 0

    def calcular_valor_total(self):
        """Calcula el valor total del movimiento"""
        if self.precio_unitario:
            self.valor_total = abs(self.cantidad) * self.precio_unitario
        return self.valor_total


class AsientoContable(db.Model):
    """Modelo para registrar asientos contables generados por movimientos de inventario"""

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    numero_asiento = db.Column(db.String(20), unique=True)

    # Información del asiento
    descripcion = db.Column(db.String(200))
    tipo_asiento = db.Column(
        db.String(30)
    )  # inventario_inicial, inventario_final, regularizacion, compra
    periodo = db.Column(db.String(7))  # YYYY-MM

    # Estado
    estado = db.Column(
        db.String(20), default="borrador"
    )  # borrador, confirmado, contabilizado

    # Control
    usuario_creacion = db.Column(db.String(50))
    fecha_contabilizacion = db.Column(db.DateTime)

    # Relaciones
    lineas = db.relationship(
        "LineaAsientoContable",
        backref="asiento",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<AsientoContable {self.numero_asiento} - {self.fecha}>"


class LineaAsientoContable(db.Model):
    """Líneas detalle de los asientos contables"""

    id = db.Column(db.Integer, primary_key=True)

    # Información contable
    cuenta_contable = db.Column(db.String(9), nullable=False)
    descripcion = db.Column(db.String(200))
    debe = db.Column(db.Float, default=0)
    haber = db.Column(db.Float, default=0)

    # Referencias
    centro_costo = db.Column(db.String(20))
    inventario_id = db.Column(db.Integer, db.ForeignKey("inventario.id"))
    movimiento_inventario_id = db.Column(
        db.Integer, db.ForeignKey("movimiento_inventario.id")
    )

    # Relación con asiento
    asiento_id = db.Column(
        db.Integer, db.ForeignKey("asiento_contable.id"), nullable=False
    )

    def __repr__(self):
        return f"<LineaAsiento {self.cuenta_contable} - D:{self.debe} H:{self.haber}>"
