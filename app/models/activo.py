from app.extensions import db
from sqlalchemy import func


class Activo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    departamento = db.Column(
        db.String(3), nullable=False
    )  # Código de departamento (000, 100, 140, etc.)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50))
    ubicacion = db.Column(db.String(100))
    estado = db.Column(db.String(50), default="Operativo")
    prioridad = db.Column(
        db.String(20), default="Media"
    )  # Campo para prioridad del activo
    fecha_adquisicion = db.Column(db.DateTime)
    ultimo_mantenimiento = db.Column(db.DateTime)
    proximo_mantenimiento = db.Column(db.DateTime)
    descripcion = db.Column(db.Text)
    modelo = db.Column(db.String(100))
    numero_serie = db.Column(db.String(100))
    fabricante = db.Column(db.String(100))
    proveedor = db.Column(
        db.String(100)
    )  # Campo para proveedor (temporal hasta crear módulo)
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    ordenes = db.relationship("OrdenTrabajo", backref="activo", lazy=True)
    planes = db.relationship("PlanMantenimiento", backref="activo", lazy=True)

    @staticmethod
    def generar_siguiente_numero():
        """Genera el siguiente número correlativo (45678)"""
        # Obtener el último número usado en cualquier activo
        ultimo_activo = db.session.query(
            func.max(func.cast(func.substr(Activo.codigo, 6, 5), db.Integer))
        ).scalar()

        if ultimo_activo:
            return str(ultimo_activo + 1).zfill(5)
        else:
            return "00001"

    @staticmethod
    def generar_codigo(departamento_codigo):
        """Genera un código completo de activo"""
        numero = Activo.generar_siguiente_numero()
        return f"{departamento_codigo}A{numero}"

    @staticmethod
    def validar_codigo(codigo):
        """Valida que el código tenga el formato correcto"""
        if len(codigo) != 9:
            return False
        if codigo[3] != "A":
            return False
        if not codigo[:3].isdigit():
            return False
        if not codigo[4:].isdigit():
            return False
        return True

    @staticmethod
    def get_departamentos():
        """Retorna la lista de departamentos disponibles"""
        return {
            "000": "General",
            "100": "Producción",
            "140": "Zona cocción",
            "150": "Envasado",
            "160": "Mantenimiento",
            "200": "Comercial",
            "300": "Calidad",
            "400": "Administración",
            "410": "RRHH",
            "500": "Logística",
            "510": "Almacén",
        }
