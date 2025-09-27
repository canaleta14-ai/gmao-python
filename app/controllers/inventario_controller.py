from app.models.inventario import Inventario, ConteoInventario, PeriodoInventario
from app.models.movimiento_inventario import (
    MovimientoInventario,
    AsientoContable,
    LineaAsientoContable,
)
from app.models.categoria import Categoria
from app.extensions import db
from flask import request
from datetime import datetime, timezone
import random
from sqlalchemy import func, extract


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
            "categoria": i.obtener_nombre_categoria(),  # Usar método del modelo
            "prefijo_categoria": i.obtener_prefijo_categoria(),
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
    # Si hay categoria_id, generar código automáticamente
    codigo = data.get("codigo")
    categoria_id = data.get("categoria_id")

    if categoria_id and not codigo:
        # Generar código automático basado en categoría
        categoria = Categoria.query.get(categoria_id)
        if categoria:
            codigo = categoria.generar_proximo_codigo()

    nuevo_item = Inventario(
        codigo=codigo or data["codigo"],
        descripcion=data["descripcion"],
        categoria_id=categoria_id,
        categoria=data.get("categoria"),  # Mantener compatibilidad
        stock_actual=data.get("stock_actual", 0),
        stock_minimo=data.get("stock_minimo", 0),
        ubicacion=data.get("ubicacion"),
        precio_unitario=data.get("precio_unitario", 0),
        unidad_medida=data.get("unidad_medida"),
        proveedor_principal=data.get("proveedor"),
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


# ========== NUEVAS FUNCIONES PARA INVENTARIOS AVANZADOS ==========


def crear_articulo_avanzado(data):
    """Crear un nuevo artículo de inventario con validaciones avanzadas"""
    errores = validar_datos_articulo(data)
    if errores:
        raise ValueError("; ".join(errores))

    articulo = Inventario(
        codigo=data["codigo"],
        descripcion=data["descripcion"],
        categoria=data.get("categoria", ""),
        stock_actual=data.get("stock_inicial", 0),
        stock_minimo=data.get("stock_minimo", 0),
        stock_maximo=data.get("stock_maximo", 100),
        ubicacion=data.get("ubicacion", ""),
        precio_unitario=data.get("precio_unitario", 0),
        costo_promedio=data.get("costo_promedio", 0),
        unidad_medida=data.get("unidad_medida", "UND"),
        proveedor=data.get("proveedor", ""),
        grupo_contable=data.get("grupo_contable", ""),
        cuenta_contable_compra=data.get("cuenta_contable_compra", "622000000"),
        requiere_conteo=data.get("requiere_conteo", True),
        critico=data.get("critico", False),
    )

    # Actualizar cuenta contable según grupo
    articulo.actualizar_cuenta_contable()

    db.session.add(articulo)
    db.session.commit()

    # Si tiene stock inicial, crear movimiento
    if data.get("stock_inicial", 0) > 0:
        crear_movimiento_inventario_avanzado(
            {
                "inventario_id": articulo.id,
                "tipo": "entrada",
                "subtipo": "inventario_inicial",
                "cantidad": data["stock_inicial"],
                "precio_unitario": data.get("precio_unitario", 0),
                "observaciones": "Stock inicial del artículo",
            }
        )

    return articulo


def listar_articulos_avanzado(filtros=None, page=1, per_page=10):
    """Listar artículos con filtros avanzados"""
    query = Inventario.query.filter_by(activo=True)

    if filtros:
        # Búsqueda general (para autocompletado)
        if "busqueda_general" in filtros and filtros["busqueda_general"]:
            search_term = filtros["busqueda_general"]
            query = query.filter(
                db.or_(
                    Inventario.codigo.ilike(f"%{search_term}%"),
                    Inventario.descripcion.ilike(f"%{search_term}%"),
                    Inventario.categoria.ilike(f"%{search_term}%"),
                    Inventario.ubicacion.ilike(f"%{search_term}%"),
                )
            )

        # Filtros específicos
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


def crear_movimiento_inventario_avanzado(data):
    """Crear un movimiento de inventario y actualizar stock"""
    errores = validar_movimiento_inventario(data)
    if errores:
        raise ValueError("; ".join(errores))

    articulo = Inventario.query.get_or_404(data["inventario_id"])

    movimiento = MovimientoInventario(
        inventario_id=data["inventario_id"],
        tipo=data["tipo"],
        subtipo=data.get("subtipo", ""),
        cantidad=data["cantidad"],
        precio_unitario=data.get("precio_unitario"),
        cuenta_contable=data.get("cuenta_contable", articulo.cuenta_contable_compra),
        centro_costo=data.get("centro_costo", ""),
        documento_referencia=data.get("documento_referencia", ""),
        observaciones=data.get("observaciones", ""),
        usuario_id=data.get("usuario_id", ""),
        orden_trabajo_id=data.get("orden_trabajo_id"),
        proveedor_id=data.get("proveedor_id"),
    )

    # Calcular valor total
    movimiento.calcular_valor_total()

    db.session.add(movimiento)

    # Actualizar stock del artículo
    if movimiento.es_entrada:
        articulo.stock_actual += abs(movimiento.cantidad)
    elif movimiento.es_salida:
        if articulo.stock_actual < abs(movimiento.cantidad):
            raise ValueError(
                f"Stock insuficiente. Stock actual: {articulo.stock_actual}"
            )
        articulo.stock_actual -= abs(movimiento.cantidad)

    # Actualizar costo promedio en entradas
    if movimiento.es_entrada and movimiento.precio_unitario:
        stock_anterior = articulo.stock_actual - abs(movimiento.cantidad)
        valor_stock_anterior = stock_anterior * (articulo.costo_promedio or 0)
        valor_entrada = abs(movimiento.cantidad) * movimiento.precio_unitario
        valor_total = valor_stock_anterior + valor_entrada
        if articulo.stock_actual > 0:
            articulo.costo_promedio = valor_total / articulo.stock_actual

    db.session.commit()
    return movimiento


def iniciar_periodo_inventario(año, mes=None):
    """Iniciar un nuevo período de inventario"""
    # Verificar que no haya otro período abierto
    periodo_abierto = PeriodoInventario.query.filter_by(
        año=año, mes=mes, estado="abierto"
    ).first()

    if periodo_abierto:
        raise ValueError("Ya existe un período de inventario abierto para este período")

    periodo = PeriodoInventario(
        año=año,
        mes=mes,
        total_articulos=Inventario.query.filter_by(
            activo=True, requiere_conteo=True
        ).count(),
    )

    db.session.add(periodo)
    db.session.commit()
    return periodo


def generar_conteos_aleatorios(cantidad=10):
    """Generar conteos aleatorios para control continuo"""
    # Seleccionar artículos aleatoriamente
    articulos = Inventario.query.filter_by(activo=True, requiere_conteo=True).all()
    if len(articulos) < cantidad:
        cantidad = len(articulos)

    articulos_seleccionados = random.sample(articulos, cantidad)
    conteos_creados = []

    for articulo in articulos_seleccionados:
        conteo = ConteoInventario(
            inventario_id=articulo.id,
            tipo_conteo="aleatorio",
            stock_teorico=articulo.stock_actual,
            usuario_conteo="sistema",
        )
        db.session.add(conteo)
        conteos_creados.append(conteo)

    db.session.commit()
    return conteos_creados


def procesar_conteo_fisico(conteo_id, stock_fisico, observaciones="", usuario=""):
    """Procesar el resultado de un conteo físico"""
    conteo = ConteoInventario.query.get_or_404(conteo_id)

    conteo.stock_fisico = stock_fisico
    conteo.diferencia = stock_fisico - conteo.stock_teorico
    conteo.observaciones = observaciones
    conteo.usuario_conteo = usuario
    conteo.estado = "validado"

    # Si hay diferencia significativa, crear movimiento de regularización
    if abs(conteo.diferencia) > 0:
        crear_movimiento_regularizacion(conteo)

    db.session.commit()
    return conteo


def crear_movimiento_regularizacion(conteo):
    """Crear movimiento de regularización por diferencia en conteo"""
    articulo = conteo.articulo

    if conteo.diferencia != 0:
        cantidad = abs(conteo.diferencia)

        movimiento = MovimientoInventario(
            inventario_id=articulo.id,
            tipo="ajuste",
            subtipo="regularizacion",
            cantidad=cantidad if conteo.diferencia > 0 else -cantidad,
            precio_unitario=articulo.costo_promedio or 0,
            observaciones=f"Regularización por conteo físico. Diferencia: {conteo.diferencia}",
            conteo_inventario_id=conteo.id,
        )

        # Actualizar stock
        articulo.stock_actual = conteo.stock_fisico

        db.session.add(movimiento)
        conteo.estado = "regularizado"


def generar_asiento_inventario_anual(año):
    """Generar asiento contable de inventario anual (stock inicial vs final)"""
    asiento = AsientoContable(
        numero_asiento=f"INV-{año}-001",
        descripcion=f"Asiento de inventario anual {año}",
        tipo_asiento="inventario_final",
        periodo=f"{año}-12",
        estado="borrador",
    )

    db.session.add(asiento)
    db.session.flush()  # Para obtener el ID

    # Obtener todos los artículos con stock
    articulos = Inventario.query.filter(
        Inventario.activo == True, Inventario.stock_actual > 0
    ).all()

    total_valor = 0

    for articulo in articulos:
        valor_stock = articulo.valor_stock
        if valor_stock > 0:
            # Línea de débito - Cuenta de inventario
            linea_debe = LineaAsientoContable(
                asiento_id=asiento.id,
                cuenta_contable="300000000",  # Cuenta de inventarios
                descripcion=f"Inventario final - {articulo.descripcion}",
                debe=valor_stock,
                inventario_id=articulo.id,
            )
            db.session.add(linea_debe)
            total_valor += valor_stock

    # Línea de crédito - Cuenta de variación de existencias
    if total_valor > 0:
        linea_haber = LineaAsientoContable(
            asiento_id=asiento.id,
            cuenta_contable="610000000",  # Variación de existencias
            descripcion=f"Variación de existencias {año}",
            haber=total_valor,
        )
        db.session.add(linea_haber)

    db.session.commit()
    return asiento


def obtener_estadisticas_inventario():
    """Obtener estadísticas generales del inventario"""
    stats = {}

    # Artículos totales
    stats["total_articulos"] = Inventario.query.filter_by(activo=True).count()

    # Artículos con stock bajo mínimo
    stats["articulos_bajo_minimo"] = Inventario.query.filter(
        Inventario.activo == True, Inventario.stock_actual <= Inventario.stock_minimo
    ).count()

    # Valor total del inventario
    valor_total = (
        db.session.query(func.sum(Inventario.stock_actual * Inventario.precio_promedio))
        .filter(Inventario.activo == True)
        .scalar()
        or 0
    )
    stats["valor_total_inventario"] = valor_total

    # Artículos críticos
    stats["articulos_criticos"] = Inventario.query.filter_by(
        activo=True, critico=True
    ).count()

    # Movimientos del mes actual
    mes_actual = datetime.now().month
    año_actual = datetime.now().year
    stats["movimientos_mes"] = MovimientoInventario.query.filter(
        extract("month", MovimientoInventario.fecha) == mes_actual,
        extract("year", MovimientoInventario.fecha) == año_actual,
    ).count()

    return stats


def validar_datos_articulo(data):
    """Validar datos de artículo"""
    errores = []

    if not data.get("codigo"):
        errores.append("El código es obligatorio")
    elif Inventario.query.filter_by(codigo=data["codigo"]).first():
        errores.append("Ya existe un artículo con este código")

    if not data.get("descripcion"):
        errores.append("La descripción es obligatoria")

    if data.get("stock_minimo", 0) < 0:
        errores.append("El stock mínimo no puede ser negativo")

    if data.get("stock_maximo", 0) < data.get("stock_minimo", 0):
        errores.append("El stock máximo debe ser mayor al mínimo")

    return errores


def validar_movimiento_inventario(data):
    """Validar datos de movimiento de inventario"""
    errores = []

    if not data.get("inventario_id"):
        errores.append("El artículo es obligatorio")

    if not data.get("tipo"):
        errores.append("El tipo de movimiento es obligatorio")

    if not data.get("cantidad") or data["cantidad"] == 0:
        errores.append("La cantidad debe ser mayor a cero")

    if data.get("precio_unitario") is not None and data["precio_unitario"] < 0:
        errores.append("El precio unitario no puede ser negativo")

    return errores
