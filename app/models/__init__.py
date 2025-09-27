# Inicialización del paquete models

from app.extensions import db

# Importar todos los modelos
from .activo import Activo
from .orden_trabajo import OrdenTrabajo
from .orden_recambio import OrdenRecambio
from .plan_mantenimiento import PlanMantenimiento
from .proveedor import Proveedor
from .inventario import Inventario
from .movimiento_inventario import MovimientoInventario
from .usuario import Usuario
from .manual import Manual
from .archivo_adjunto import ArchivoAdjunto

# Exportar para fácil importación
__all__ = [
    "db",
    "Activo",
    "OrdenTrabajo",
    "OrdenRecambio",
    "PlanMantenimiento",
    "Proveedor",
    "Inventario",
    "MovimientoInventario",
    "Usuario",
    "Manual",
    "ArchivoAdjunto",
]
