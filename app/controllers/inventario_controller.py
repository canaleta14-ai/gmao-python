from app.models.inventario import Inventario
from app.models.movimiento_inventario import MovimientoInventario
from app.extensions import db


def listar_inventario():
    items = Inventario.query.all()
    return [
        {
            "id": i.id,
            "codigo": i.codigo,
            "descripcion": i.descripcion,
            "categoria": i.categoria,
            "stock_actual": i.stock_actual,
            "stock_minimo": i.stock_minimo,
            "ubicacion": i.ubicacion,
            "precio_unitario": i.precio_unitario,
            "estado": (
                "Normal"
                if i.stock_actual > i.stock_minimo
                else "Stock Bajo" if i.stock_actual > 0 else "Sin Stock"
            ),
        }
        for i in items
    ]


def crear_item(data):
    nuevo_item = Inventario(
        codigo=data["codigo"],
        descripcion=data["descripcion"],
        categoria=data.get("categoria"),
        stock_actual=data.get("stock_actual", 0),
        stock_minimo=data.get("stock_minimo", 0),
        ubicacion=data.get("ubicacion"),
        precio_unitario=data.get("precio_unitario", 0),
        unidad_medida=data.get("unidad_medida"),
        proveedor=data.get("proveedor"),
    )
    db.session.add(nuevo_item)
    db.session.commit()
    return nuevo_item


def registrar_movimiento(id, data):
    item = Inventario.query.get_or_404(id)
    movimiento = MovimientoInventario(
        tipo=data["tipo"],
        cantidad=data["cantidad"],
        precio=data.get("precio"),
        observaciones=data.get("observaciones"),
        inventario_id=id,
        orden_trabajo_id=data.get("orden_trabajo_id"),
    )
    if data["tipo"] == "Entrada":
        item.stock_actual += data["cantidad"]
    else:
        item.stock_actual -= data["cantidad"]
    db.session.add(movimiento)
    db.session.commit()
    return movimiento
