from app.models.inventario import Inventario
from app.models.movimiento_inventario import MovimientoInventario
from app.extensions import db
from flask import request


def listar_inventario():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    search = request.args.get("q", "", type=str)

    query = Inventario.query

    # Aplicar filtros de búsqueda
    if search:
        query = query.filter(
            db.or_(
                Inventario.codigo.ilike(f"%{search}%"),
                Inventario.descripcion.ilike(f"%{search}%"),
                Inventario.categoria.ilike(f"%{search}%"),
                Inventario.ubicacion.ilike(f"%{search}%"),
            )
        )

    # Paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    items = pagination.items

    # Función para determinar estado
    def get_estado(item):
        if item.stock_actual > item.stock_minimo:
            return "Disponible"
        elif item.stock_actual > 0:
            return "Bajo Stock"
        else:
            return "Sin Stock"

    items_data = [
        {
            "id": i.id,
            "codigo": i.codigo,
            "descripcion": i.descripcion,
            "categoria": i.categoria,
            "stock_actual": i.stock_actual,
            "stock_minimo": i.stock_minimo,
            "ubicacion": i.ubicacion,
            "precio_unitario": i.precio_unitario,
            "estado": get_estado(i),
        }
        for i in items
    ]

    return {
        "items": items_data,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }


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
