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

        # Filtro de búsqueda general (para autocompletado)
        if "busqueda_general" in filtros and filtros["busqueda_general"]:
            busqueda = filtros["busqueda_general"]
            query = query.filter(
                db.or_(
                    Inventario.codigo.ilike(f"%{busqueda}%"),
                    Inventario.descripcion.ilike(f"%{busqueda}%"),
                    Inventario.categoria.ilike(f"%{busqueda}%"),
                    Inventario.ubicacion.ilike(f"%{busqueda}%"),
                )
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


def exportar_inventario_csv():
    """Genera un archivo CSV con todos los artículos del inventario"""
    from io import StringIO
    import csv

    articulos = Inventario.query.filter_by(activo=True).all()

    output = StringIO()
    writer = csv.writer(output)

    # Escribir encabezados
    writer.writerow(
        [
            "Código",
            "Descripción",
            "Categoría",
            "Stock Actual",
            "Stock Mínimo",
            "Stock Máximo",
            "Ubicación",
            "Precio Unitario",
            "Precio Promedio",
            "Valor Stock",
            "Unidad Medida",
            "Proveedor Principal",
            "Cuenta Contable",
            "Grupo Contable",
            "Crítico",
            "Fecha Creación",
        ]
    )

    # Escribir datos
    for articulo in articulos:
        writer.writerow(
            [
                articulo.codigo,
                articulo.descripcion,
                articulo.categoria or "",
                articulo.stock_actual,
                articulo.stock_minimo,
                articulo.stock_maximo or "",
                articulo.ubicacion or "",
                articulo.precio_unitario,
                articulo.precio_promedio,
                (
                    articulo.stock_actual * articulo.precio_promedio
                    if articulo.precio_promedio
                    else 0
                ),
                articulo.unidad_medida,
                articulo.proveedor_principal or "",
                articulo.cuenta_contable_compra,
                articulo.grupo_contable or "",
                "Sí" if articulo.critico else "No",
                (
                    articulo.fecha_creacion.strftime("%d/%m/%Y")
                    if articulo.fecha_creacion
                    else ""
                ),
            ]
        )

    csv_data = output.getvalue()
    output.close()

    return csv_data


# Funciones para movimientos de inventario
from app.models.movimiento_inventario import MovimientoInventario
from app.models.usuario import Usuario


def registrar_movimiento_inventario(data):
    """Registrar un nuevo movimiento de inventario"""
    try:
        # Validar datos requeridos
        required_fields = ["inventario_id", "tipo", "cantidad"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Campo requerido faltante: {field}")

        # Obtener el artículo
        articulo = Inventario.query.get(data["inventario_id"])
        if not articulo:
            raise ValueError("Artículo no encontrado")

        # Crear el movimiento
        movimiento = MovimientoInventario(
            inventario_id=data["inventario_id"],
            tipo=data["tipo"],
            subtipo=data.get("subtipo"),
            cantidad=data["cantidad"],
            precio_unitario=data.get("precio_unitario"),
            valor_total=data.get("valor_total"),
            cuenta_contable=data.get(
                "cuenta_contable", articulo.cuenta_contable_compra
            ),
            centro_costo=data.get("centro_costo"),
            documento_referencia=data.get("documento_referencia"),
            observaciones=data.get("observaciones"),
            usuario_id=data.get("usuario_id", "sistema"),
        )

        # Actualizar stock del artículo según el tipo de movimiento
        if movimiento.tipo == "entrada":
            articulo.stock_actual += movimiento.cantidad
        elif movimiento.tipo == "salida":
            if articulo.stock_actual < movimiento.cantidad:
                raise ValueError("Stock insuficiente para la salida")
            articulo.stock_actual -= movimiento.cantidad
        elif movimiento.tipo == "ajuste":
            # Para ajustes, la cantidad puede ser positiva o negativa
            articulo.stock_actual += movimiento.cantidad
        elif movimiento.tipo == "regularizacion":
            # Regularización suma al stock (corrige inventario)
            articulo.stock_actual += movimiento.cantidad

        # Calcular valor total si no se proporciona
        if not movimiento.valor_total and movimiento.precio_unitario:
            movimiento.valor_total = movimiento.precio_unitario * abs(
                movimiento.cantidad
            )

        db.session.add(movimiento)
        db.session.commit()

        return movimiento

    except Exception as e:
        db.session.rollback()
        raise e


def obtener_movimientos_articulo(articulo_id, page=1, per_page=10):
    """Obtener historial de movimientos de un artículo"""
    try:
        query = MovimientoInventario.query.filter_by(inventario_id=articulo_id)
        query = query.order_by(MovimientoInventario.fecha.desc())

        # Paginación
        movimientos = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "movimientos": [
                {
                    "id": m.id,
                    "fecha": m.fecha.strftime("%d/%m/%Y %H:%M") if m.fecha else "",
                    "tipo": m.tipo,
                    "subtipo": m.subtipo,
                    "cantidad": m.cantidad,
                    "precio_unitario": m.precio_unitario,
                    "valor_total": m.valor_total,
                    "cuenta_contable": m.cuenta_contable,
                    "documento_referencia": m.documento_referencia,
                    "observaciones": m.observaciones,
                    "usuario_id": m.usuario_id,
                }
                for m in movimientos.items
            ],
            "page": movimientos.page,
            "per_page": movimientos.per_page,
            "total": movimientos.total,
            "pages": movimientos.pages,
        }

    except Exception as e:
        raise e


def obtener_movimientos_generales(filtros=None, page=1, per_page=10):
    """Obtener vista general de movimientos con filtros"""
    try:
        query = MovimientoInventario.query

        # Aplicar filtros
        if filtros:
            if "tipo" in filtros:
                query = query.filter_by(tipo=filtros["tipo"])
            if "fecha_desde" in filtros:
                query = query.filter(
                    MovimientoInventario.fecha >= filtros["fecha_desde"]
                )
            if "fecha_hasta" in filtros:
                query = query.filter(
                    MovimientoInventario.fecha <= filtros["fecha_hasta"]
                )
            if "usuario_id" in filtros:
                query = query.filter_by(usuario_id=filtros["usuario_id"])

        # Unir con información del artículo
        query = query.join(Inventario).add_columns(
            Inventario.codigo, Inventario.descripcion, Inventario.unidad_medida
        )

        query = query.order_by(MovimientoInventario.fecha.desc())

        # Paginación
        movimientos = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "movimientos": [
                {
                    "id": m.MovimientoInventario.id,
                    "fecha": (
                        m.MovimientoInventario.fecha.strftime("%d/%m/%Y %H:%M")
                        if m.MovimientoInventario.fecha
                        else ""
                    ),
                    "tipo": m.MovimientoInventario.tipo,
                    "subtipo": m.MovimientoInventario.subtipo,
                    "cantidad": m.MovimientoInventario.cantidad,
                    "codigo_articulo": m.codigo,
                    "descripcion_articulo": m.descripcion,
                    "unidad_medida": m.unidad_medida,
                    "precio_unitario": m.MovimientoInventario.precio_unitario,
                    "valor_total": m.MovimientoInventario.valor_total,
                    "documento_referencia": m.MovimientoInventario.documento_referencia,
                    "usuario_id": m.MovimientoInventario.usuario_id,
                }
                for m in movimientos.items
            ],
            "page": movimientos.page,
            "per_page": movimientos.per_page,
            "total": movimientos.total,
            "pages": movimientos.pages,
        }

    except Exception as e:
        raise e


def editar_articulo_simple(articulo_id, data):
    """Editar un artículo existente"""
    try:
        articulo = Inventario.query.get(articulo_id)
        if not articulo:
            raise ValueError("Artículo no encontrado")

        # Campos que se pueden editar
        campos_editables = [
            "codigo",
            "descripcion",
            "categoria",
            "subcategoria",
            "ubicacion",
            "stock_minimo",
            "stock_maximo",
            "unidad_medida",
            "precio_unitario",
            "proveedor_principal",
            "cuenta_contable_compra",
            "grupo_contable",
            "critico",
            "activo",
            "observaciones",
        ]

        for campo in campos_editables:
            if campo in data:
                setattr(articulo, campo, data[campo])

        articulo.fecha_actualizacion = datetime.now(timezone.utc)

        db.session.commit()
        return articulo

    except Exception as e:
        db.session.rollback()
        raise e
