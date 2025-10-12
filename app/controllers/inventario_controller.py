from app.models.inventario import Inventario, ConteoInventario, PeriodoInventario
from app.models.movimiento_inventario import (
    MovimientoInventario,
    AsientoContable,
    LineaAsientoContable,
)
from app.models.categoria import Categoria
from app.extensions import db
from flask import request
from datetime import datetime, timezone, timedelta
import random
import logging
from sqlalchemy import func, extract

logger = logging.getLogger(__name__)


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
    # Permitir que el frontend envíe `categoria_id` o `categoria` (id como string)
    categoria_id = data.get("categoria_id") or data.get("categoria")
    try:
        # Normalizar a entero si viene como string
        categoria_id = int(categoria_id) if categoria_id not in (None, "") else None
    except (ValueError, TypeError):
        # Si no es convertible (por ejemplo, nombre de categoría), mantener None
        categoria_id = None

    if categoria_id and not codigo:
        # Generar código automático basado en categoría
        categoria = Categoria.query.get(categoria_id)
        if categoria:
            codigo = categoria.generar_proximo_codigo()

    # Si no hay código y tampoco categoría para generarlo, validar explícitamente
    if not codigo and not categoria_id:
        raise ValueError(
            "El código es obligatorio si no se ha seleccionado una categoría"
        )

    nuevo_item = Inventario(
        codigo=codigo,
        descripcion=data["descripcion"],
        categoria_id=categoria_id,
        # Mantener compatibilidad: si `categoria` fue un nombre, almacenarlo
        categoria=(
            data.get("categoria") if isinstance(data.get("categoria"), str) else None
        ),
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
    from app.services.servicio_fifo import ServicioFIFO
    from datetime import datetime, timedelta

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

        # 🆕 CREACIÓN AUTOMÁTICA DE LOTE FIFO para entradas
        try:
            # Generar código de lote automático
            from datetime import datetime

            fecha_hoy = datetime.now()
            codigo_lote = f"{articulo.codigo}-{fecha_hoy.strftime('%Y%m%d')}-{movimiento.id or 'AUTO'}"

            # Calcular fecha de vencimiento estimada (si no se proporciona)
            fecha_vencimiento = data.get("fecha_vencimiento")
            if not fecha_vencimiento and articulo.categoria:
                # Asignar vencimiento por defecto según categoría
                dias_vencimiento = {
                    "medicamentos": 365,
                    "quimicos": 180,
                    "repuestos": 1095,  # 3 años
                    "consumibles": 365,
                    "herramientas": 1825,  # 5 años
                }.get(
                    articulo.categoria.lower(), 730
                )  # 2 años por defecto

                fecha_vencimiento = fecha_hoy + timedelta(days=dias_vencimiento)

            # Crear lote FIFO automáticamente
            lote_fifo = ServicioFIFO.crear_lote_entrada(
                inventario_id=articulo.id,
                cantidad=abs(movimiento.cantidad),
                precio_unitario=movimiento.precio_unitario or 0,
                codigo_lote=codigo_lote,
                fecha_vencimiento=fecha_vencimiento,
                documento_origen=movimiento.documento_referencia,
                proveedor_id=movimiento.proveedor_id,
                usuario_id=movimiento.usuario_id or "sistema",
                observaciones=f"Lote creado automáticamente por entrada de inventario. {movimiento.observaciones or ''}",
            )

            logger.info(
                f"✅ Lote FIFO creado automáticamente: {lote_fifo.id} para artículo {articulo.codigo}"
            )

        except Exception as e:
            logger.error(f"❌ Error al crear lote FIFO automático: {str(e)}")
            # No fallar la entrada por error en lote, solo registrar

    elif movimiento.es_salida:
        # 🆕 CONSUMO AUTOMÁTICO FIFO para salidas
        try:
            if articulo.stock_actual < abs(movimiento.cantidad):
                raise ValueError(
                    f"Stock insuficiente. Stock actual: {articulo.stock_actual}"
                )

            # Usar ServicioFIFO para consumir automáticamente
            consumos, cantidad_faltante = ServicioFIFO.consumir_fifo(
                inventario_id=articulo.id,
                cantidad_total=abs(movimiento.cantidad),
                orden_trabajo_id=movimiento.orden_trabajo_id,
                documento_referencia=movimiento.documento_referencia,
                usuario_id=movimiento.usuario_id or "sistema",
                observaciones=f"Consumo automático por salida de inventario. {movimiento.observaciones or ''}",
            )

            if cantidad_faltante > 0:
                logger.warning(
                    f"⚠️ Cantidad faltante en FIFO: {cantidad_faltante} para artículo {articulo.codigo}"
                )

            logger.info(
                f"✅ Consumo FIFO automático: {len(consumos)} lotes afectados para artículo {articulo.codigo}"
            )

        except Exception as e:
            logger.error(f"❌ Error en consumo FIFO automático: {str(e)}")
            # Continuar con el método tradicional

        articulo.stock_actual -= abs(movimiento.cantidad)

    # Actualizar costo promedio en entradas
    if movimiento.es_entrada and movimiento.precio_unitario:
        stock_anterior = articulo.stock_actual - abs(movimiento.cantidad)
        valor_stock_anterior = stock_anterior * (articulo.precio_promedio or 0)
        valor_entrada = abs(movimiento.cantidad) * movimiento.precio_unitario
        valor_total = valor_stock_anterior + valor_entrada
        if articulo.stock_actual > 0:
            articulo.precio_promedio = valor_total / articulo.stock_actual

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
    # Seleccionar artículos aleatoriamente (solo activos)
    articulos = Inventario.query.filter_by(activo=True).all()
    if len(articulos) < cantidad:
        cantidad = len(articulos)

    articulos_seleccionados = random.sample(articulos, cantidad)
    conteos_creados = []

    for articulo in articulos_seleccionados:
        conteo = ConteoInventario(
            inventario_id=articulo.id,
            tipo_conteo="aleatorio",
            stock_teorico=(
                int(float(articulo.stock_actual)) if articulo.stock_actual else 0
            ),
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


def editar_conteo(conteo_id, stock_fisico, observaciones="", usuario_conteo=""):
    """Editar un conteo físico existente"""
    conteo = ConteoInventario.query.get_or_404(conteo_id)

    # Solo permitir editar conteos que no estén ya procesados/regularizados
    if conteo.estado == "regularizado":
        raise ValueError("No se puede editar un conteo ya regularizado")

    # Actualizar los campos
    conteo.stock_fisico = stock_fisico
    conteo.diferencia = stock_fisico - conteo.stock_teorico
    conteo.observaciones = observaciones
    conteo.usuario_conteo = usuario_conteo

    # Si el conteo estaba pendiente y ahora tiene stock_fisico, marcarlo como validado
    if conteo.estado == "pendiente" and stock_fisico is not None:
        conteo.estado = "validado"

    db.session.commit()
    return conteo


def crear_movimiento_regularizacion(conteo):
    """Crear movimiento de regularización por diferencia en conteo"""
    articulo = conteo.articulo

    if conteo.diferencia != 0:
        cantidad = abs(conteo.diferencia)
        precio_unitario = float(articulo.precio_promedio or 0)

        movimiento = MovimientoInventario(
            inventario_id=articulo.id,
            tipo="ajuste",
            subtipo="regularizacion",
            cantidad=cantidad if conteo.diferencia > 0 else -cantidad,
            precio_unitario=precio_unitario,
            valor_total=cantidad * precio_unitario,
            observaciones=f"Regularización por conteo físico. Diferencia: {conteo.diferencia}",
            conteo_inventario_id=conteo.id,
        )

        # Actualizar stock del artículo
        articulo.stock_actual = int(conteo.stock_fisico)

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
    try:
        # Artículos totales
        stats["total_articulos"] = Inventario.query.filter_by(activo=True).count()

        # Artículos con stock bajo mínimo
        stats["articulos_bajo_minimo"] = Inventario.query.filter(
            Inventario.activo == True,
            Inventario.stock_actual <= Inventario.stock_minimo,
        ).count()

        # Valor total del inventario
        valor_total = (
            db.session.query(
                func.sum(Inventario.stock_actual * Inventario.precio_promedio)
            )
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
    except Exception:
        # Limpiar sesión en caso de estado abortado
        try:
            db.session.rollback()
        except Exception:
            pass
        try:
            db.session.remove()
        except Exception:
            pass

        # Fallback mínimo: contar totales vía SQL directo en AUTOCOMMIT
        total = 0
        try:
            backend = (
                db.engine.url.get_backend_name()
                if getattr(db, "engine", None)
                else None
            )
            table_name = "inventario"
            if backend == "postgresql":
                table_name = "public.inventario"
            with db.engine.connect() as base_conn:
                try:
                    base_conn.exec_driver_sql("ROLLBACK")
                except Exception:
                    pass
                with base_conn.execution_options(isolation_level="AUTOCOMMIT") as conn:
                    res = conn.execute(
                        db.text(f"SELECT COUNT(*) AS total FROM {table_name}")
                    ).first()
                    total = int(res[0]) if res else 0
        except Exception:
            total = 0

        return {
            "total_articulos": total,
            "articulos_bajo_minimo": 0,
            "valor_total_inventario": 0,
            "articulos_criticos": 0,
            "movimientos_mes": 0,
        }


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
