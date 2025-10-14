from app.extensions import db
from datetime import datetime, timezone
from decimal import Decimal


class LoteInventario(db.Model):
    """
    Modelo para implementar control FIFO (First In, First Out) en el inventario.
    Cada entrada de stock crea un nuevo lote con fecha y cantidad específica.
    """

    __tablename__ = "lote_inventario"

    id = db.Column(db.Integer, primary_key=True)

    # Relación con el artículo de inventario
    inventario_id = db.Column(
        db.Integer, db.ForeignKey("inventario.id"), nullable=False
    )

    # Información del lote
    codigo_lote = db.Column(db.String(50), nullable=True)  # Código opcional del lote
    fecha_entrada = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    fecha_vencimiento = db.Column(
        db.DateTime, nullable=True
    )  # Para artículos perecederos

    # Cantidades
    cantidad_inicial = db.Column(
        db.Numeric(12, 4), nullable=False
    )  # Cantidad original del lote
    cantidad_actual = db.Column(
        db.Numeric(12, 4), nullable=False
    )  # Cantidad disponible actual
    cantidad_reservada = db.Column(
        db.Numeric(12, 4), default=0
    )  # Cantidad reservada para órdenes

    # Información económica
    precio_unitario = db.Column(
        db.Numeric(10, 2), nullable=False
    )  # Precio al que se compró
    costo_total = db.Column(db.Numeric(10, 2), nullable=False)  # Costo total del lote

    # Referencias de origen
    documento_origen = db.Column(
        db.String(50), nullable=True
    )  # Factura, orden de compra, etc.
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedor.id"), nullable=True)
    movimiento_entrada_id = db.Column(
        db.Integer, db.ForeignKey("movimiento_inventario.id"), nullable=True
    )

    # Control y estado
    activo = db.Column(db.Boolean, default=True)
    observaciones = db.Column(db.Text, nullable=True)

    # Metadatos
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    usuario_creacion = db.Column(db.String(50))
    fecha_modificacion = db.Column(
        db.DateTime, onupdate=lambda: datetime.now(timezone.utc)
    )
    usuario_modificacion = db.Column(db.String(50))

    # Relaciones
    inventario = db.relationship("Inventario", backref="lotes")
    movimientos = db.relationship("MovimientoLote", backref="lote", lazy=True)

    def __repr__(self):
        return f"<LoteInventario {self.codigo_lote or self.id} - {self.cantidad_actual}/{self.cantidad_inicial}>"

    @property
    def esta_agotado(self):
        """Indica si el lote está completamente consumido"""
        return float(self.cantidad_actual) <= 0

    @property
    def cantidad_disponible(self):
        """Cantidad disponible para consumo (actual - reservada)"""
        return float(self.cantidad_actual) - float(self.cantidad_reservada)

    @property
    def esta_vencido(self):
        """Indica si el lote está vencido"""
        if not self.fecha_vencimiento:
            return False
        return datetime.now(timezone.utc) > self.fecha_vencimiento

    @property
    def dias_hasta_vencimiento(self):
        """Días hasta el vencimiento (None si no tiene fecha de vencimiento)"""
        if not self.fecha_vencimiento:
            return None
        delta = self.fecha_vencimiento - datetime.now(timezone.utc)
        return delta.days

    def consumir(self, cantidad):
        """
        Consume cantidad del lote siguiendo FIFO.
        Retorna la cantidad realmente consumida.
        """
        if cantidad <= 0:
            return 0

        cantidad_consumible = min(float(cantidad), self.cantidad_disponible)
        if cantidad_consumible <= 0:
            return 0

        self.cantidad_actual -= Decimal(str(cantidad_consumible))
        return cantidad_consumible

    def reservar(self, cantidad):
        """
        Reserva cantidad del lote para una orden.
        Retorna la cantidad realmente reservada.
        """
        if cantidad <= 0:
            return 0

        cantidad_reservable = min(float(cantidad), self.cantidad_disponible)
        if cantidad_reservable <= 0:
            return 0

        self.cantidad_reservada += Decimal(str(cantidad_reservable))
        return cantidad_reservable

    def liberar_reserva(self, cantidad):
        """
        Libera cantidad reservada del lote.
        """
        if cantidad <= 0:
            return

        cantidad_a_liberar = min(float(cantidad), float(self.cantidad_reservada))
        self.cantidad_reservada -= Decimal(str(cantidad_a_liberar))
        return cantidad_a_liberar

    @staticmethod
    def obtener_lotes_fifo(inventario_id, cantidad_necesaria):
        """
        Obtiene los lotes necesarios siguiendo orden FIFO para una cantidad específica.
        Retorna lista de tuplas (lote, cantidad_a_consumir).
        """
        lotes = (
            LoteInventario.query.filter_by(inventario_id=inventario_id, activo=True)
            .filter(LoteInventario.cantidad_actual > 0)
            .order_by(
                LoteInventario.fecha_entrada.asc()  # FIFO: primero los más antiguos
            )
            .all()
        )

        resultado = []
        cantidad_pendiente = float(cantidad_necesaria)

        for lote in lotes:
            if cantidad_pendiente <= 0:
                break

            cantidad_disponible = lote.cantidad_disponible
            if cantidad_disponible <= 0:
                continue

            cantidad_a_tomar = min(cantidad_pendiente, cantidad_disponible)
            resultado.append((lote, cantidad_a_tomar))
            cantidad_pendiente -= cantidad_a_tomar

        return resultado, cantidad_pendiente


class MovimientoLote(db.Model):
    """
    Modelo para registrar movimientos específicos de lotes de inventario.
    Permite trazabilidad completa de cada lote.
    """

    __tablename__ = "movimiento_lote"

    id = db.Column(db.Integer, primary_key=True)

    # Relaciones
    lote_id = db.Column(db.Integer, db.ForeignKey("lote_inventario.id"), nullable=False)
    movimiento_inventario_id = db.Column(
        db.Integer, db.ForeignKey("movimiento_inventario.id"), nullable=True
    )
    orden_trabajo_id = db.Column(
        db.Integer, db.ForeignKey("orden_trabajo.id"), nullable=True
    )

    # Información del movimiento
    tipo_movimiento = db.Column(
        db.String(20), nullable=False
    )  # consumo, reserva, liberacion, ajuste
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_movimiento = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Referencias
    documento_referencia = db.Column(db.String(50), nullable=True)
    observaciones = db.Column(db.Text, nullable=True)

    # Control
    usuario_id = db.Column(db.String(50))

    def __repr__(self):
        return f"<MovimientoLote {self.tipo_movimiento} - {self.cantidad} - Lote {self.lote_id}>"
