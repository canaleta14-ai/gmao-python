from app.extensions import db
from datetime import datetime, timezone


class Inventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)

    # Relación con categoría (nueva estructura)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=True)

    # Mantener campo categoria string para compatibilidad hacia atrás
    categoria = db.Column(db.String(100))
    subcategoria = db.Column(db.String(100))
    ubicacion = db.Column(db.String(100))

    # Stock - usando DECIMAL para mayor precisión
    stock_actual = db.Column(db.Numeric(10, 2), default=0)
    stock_minimo = db.Column(db.Numeric(10, 2), default=0)
    stock_maximo = db.Column(db.Numeric(10, 2))
    unidad_medida = db.Column(db.String(20), default="UNI")

    # Precios y costos - usando DECIMAL
    precio_unitario = db.Column(db.Numeric(10, 2), default=0)
    precio_promedio = db.Column(db.Numeric(10, 2), default=0)

    # Información del proveedor
    proveedor_principal = db.Column(db.String(100))

    # Configuración contable
    cuenta_contable_compra = db.Column(db.String(20), default="622000000")
    grupo_contable = db.Column(db.String(10))

    # Control de inventario
    critico = db.Column(db.Boolean, default=False)
    activo = db.Column(db.Boolean, default=True)

    # Campos adicionales
    observaciones = db.Column(db.Text)

    # Metadatos
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_actualizacion = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relaciones
    movimientos = db.relationship("MovimientoInventario", backref="articulo", lazy=True)
    conteos = db.relationship("ConteoInventario", backref="articulo", lazy=True)
    categoria_obj = db.relationship("Categoria", back_populates="articulos", lazy=True)

    def __repr__(self):
        return f"<Inventario {self.codigo}: {self.descripcion}>"

    @property
    def valor_stock(self):
        """Calcula el valor total del stock actual"""
        if self.stock_actual and self.precio_promedio:
            return float(self.stock_actual) * float(self.precio_promedio)
        return 0

    @property
    def necesita_reposicion(self):
        """Indica si el artículo necesita reposición"""
        return self.stock_actual <= self.stock_minimo

    def actualizar_cuenta_contable(self):
        """Actualiza la cuenta contable según el grupo"""
        if self.grupo_contable == "60":
            # Para materias primas o envases, se debe especificar otra cuenta
            if (
                not self.cuenta_contable_compra
                or self.cuenta_contable_compra == "622000000"
            ):
                self.cuenta_contable_compra = "600000000"  # Cuenta por defecto grupo 60
        else:
            self.cuenta_contable_compra = "622000000"  # Cuenta predeterminada

    def generar_codigo_categoria(self, categoria_id):
        """Genera un código automático basado en la categoría seleccionada"""
        from .categoria import Categoria

        if categoria_id:
            categoria = Categoria.query.get(categoria_id)
            if categoria:
                codigo = categoria.generar_proximo_codigo()
                return codigo
        return None

    def obtener_nombre_categoria(self):
        """Obtiene el nombre de la categoría (prioriza la nueva estructura)"""
        if self.categoria_obj:
            return self.categoria_obj.nombre
        return self.categoria or "Sin categoría"

    def obtener_prefijo_categoria(self):
        """Obtiene el prefijo de la categoría"""
        if self.categoria_obj:
            return self.categoria_obj.prefijo
        return ""


class ConteoInventario(db.Model):
    """Modelo para registrar conteos de inventario"""

    id = db.Column(db.Integer, primary_key=True)
    fecha_conteo = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    tipo_conteo = db.Column(db.String(20))  # 'mensual', 'aleatorio', 'anual'

    # Datos del conteo
    stock_teorico = db.Column(db.Integer)
    stock_fisico = db.Column(db.Integer)
    diferencia = db.Column(db.Integer)  # stock_fisico - stock_teorico

    # Control
    usuario_conteo = db.Column(db.String(50))
    observaciones = db.Column(db.Text)
    estado = db.Column(
        db.String(20), default="pendiente"
    )  # pendiente, validado, regularizado

    # Relaciones
    inventario_id = db.Column(
        db.Integer, db.ForeignKey("inventario.id"), nullable=False
    )
    periodo_inventario_id = db.Column(
        db.Integer, db.ForeignKey("periodo_inventario.id")
    )

    def __repr__(self):
        return f"<ConteoInventario {self.inventario_id} - {self.fecha_conteo}>"

    @property
    def porcentaje_diferencia(self):
        """Calcula el porcentaje de diferencia"""
        if self.stock_teorico > 0:
            return (self.diferencia / self.stock_teorico) * 100
        return 0


class PeriodoInventario(db.Model):
    """Modelo para manejar inventarios periódicos (mensual/anual)"""

    id = db.Column(db.Integer, primary_key=True)
    año = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer)  # NULL para inventario anual

    # Control del proceso
    fecha_inicio = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_fin = db.Column(db.DateTime)
    estado = db.Column(
        db.String(20), default="abierto"
    )  # abierto, cerrado, regularizado

    # Estadísticas
    total_articulos = db.Column(db.Integer, default=0)
    articulos_contados = db.Column(db.Integer, default=0)
    articulos_con_diferencias = db.Column(db.Integer, default=0)
    valor_total_diferencias = db.Column(db.Float, default=0)

    # Usuario responsable
    usuario_responsable = db.Column(db.String(50))
    observaciones = db.Column(db.Text)

    # Relaciones
    conteos = db.relationship("ConteoInventario", backref="periodo", lazy=True)

    def __repr__(self):
        periodo = f"{self.año}-{self.mes:02d}" if self.mes else f"{self.año}"
        return f"<PeriodoInventario {periodo}>"

    @property
    def porcentaje_completado(self):
        """Calcula el porcentaje de artículos contados"""
        if self.total_articulos > 0:
            return (self.articulos_contados / self.total_articulos) * 100
        return 0
