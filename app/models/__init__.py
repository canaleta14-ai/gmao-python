# Inicialización del paquete models

from app.extensions import db

# Importar todos los modelos
from .activo import Activo
from .orden_trabajo import OrdenTrabajo
from .plan_mantenimiento import PlanMantenimiento
from .proveedor import Proveedor
from .inventario import Inventario
from .movimiento_inventario import MovimientoInventario
from .usuario import Usuario
from .manual import Manual

# Exportar para fácil importación
__all__ = [
    "db",
    "Activo",
    "OrdenTrabajo",
    "PlanMantenimiento",
    "Proveedor",
    "Inventario",
    "MovimientoInventario",
    "Usuario",
    "Manual",
]
