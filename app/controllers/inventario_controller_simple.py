from app.models.inventario import Inventario
from app.extensions import db
from flask import request
from datetime import datetime, timezone
from sqlalchemy import func


def obtener_estadisticas_inventario():
    """Obtener estadísticas generales del inventario"""
    stats = {}

    # Artículos totales
    stats["total_articulos"] = Inventario.query.filter_by(activo=True).count()

    # Artículos con stock bajo mínimo
    stats["articulos_bajo_minimo"] = Inventario.query.filter(
        Inventario.activo == True, Inventario.stock_actual <= Inventario.stock_minimo
    ).count()

    # Valor total del inventario usando precio_promedio
    valor_total = (
        db.session.query(func.sum(Inventario.stock_actual * Inventario.precio_promedio))
        .filter(Inventario.activo == True)
        .scalar()
        or 0
    )
    stats["valor_total_stock"] = float(valor_total) if valor_total else 0

    # Artículos críticos
    stats["articulos_criticos"] = Inventario.query.filter_by(
        activo=True, critico=True
    ).count()

    return stats


def listar_articulos_avanzado(filtros=None, page=1, per_page=10):
    """Listar artículos con filtros avanzados"""
    query = Inventario.query.filter_by(activo=True)

    if filtros:
        if "codigo" in filtros and filtros["codigo"]:
            query = query.filter(Inventario.codigo.ilike(f"%{filtros['codigo']}%"))
        if "descripcion" in filtros and filtros["descripcion"]:
            query = query.filter(
                Inventario.descripcion.ilike(f"%{filtros['descripcion']}%")
            )
        if "categoria" in filtros and filtros["categoria"]:
            query = query.filter(Inventario.categoria == filtros["categoria"])
        if "bajo_minimo" in filtros and filtros["bajo_minimo"]:
            query = query.filter(Inventario.stock_actual <= Inventario.stock_minimo)
        if "critico" in filtros and filtros["critico"] == "true":
            query = query.filter(Inventario.critico == True)
        if "ubicacion" in filtros and filtros["ubicacion"]:
            query = query.filter(
                Inventario.ubicacion.ilike(f"%{filtros['ubicacion']}%")
            )

    paginacion = query.order_by(Inventario.codigo).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return paginacion.items, paginacion.total


def crear_articulo_simple(data):
    """Crear un nuevo artículo de inventario simple"""
    # Validar que el código no exista
    if Inventario.query.filter_by(codigo=data["codigo"]).first():
        raise ValueError("Ya existe un artículo con este código")

    articulo = Inventario(
        codigo=data["codigo"],
        descripcion=data["descripcion"],
        categoria=data.get("categoria", ""),
        stock_actual=data.get("stock_actual", 0),
        stock_minimo=data.get("stock_minimo", 0),
        stock_maximo=data.get("stock_maximo", 100),
        ubicacion=data.get("ubicacion", ""),
        precio_unitario=data.get("precio_unitario", 0),
        precio_promedio=data.get("precio_promedio", 0),
        unidad_medida=data.get("unidad_medida", "UNI"),
        proveedor_principal=data.get("proveedor_principal", ""),
        grupo_contable=data.get("grupo_contable", ""),
        cuenta_contable_compra=data.get("cuenta_contable_compra", "622000000"),
        critico=data.get("critico", False),
        activo=data.get("activo", True),
        observaciones=data.get("observaciones", ""),
    )

    db.session.add(articulo)
    db.session.commit()
    return articulo
