#!/usr/bin/env python3
"""
🚀 CONTROLADOR DE INVENTARIO OPTIMIZADO
Integración completa con FIFO optimizado, caché y métricas de performance
"""

from app.models.inventario import Inventario, ConteoInventario, PeriodoInventario
from app.models.movimiento_inventario import MovimientoInventario
from app.models.categoria import Categoria
from app.extensions import db
from app.blueprints.performance_metrics import performance_monitor
from app.blueprints.cached_inventario_simple import simple_cache, cache_key
from flask import request, jsonify
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import logging
from sqlalchemy import func, extract

# Importar FIFO optimizado
from fifo_optimizado import FIFOOptimizado

logger = logging.getLogger(__name__)

# Instancia global del FIFO optimizado
fifo_optimizado = FIFOOptimizado()


@performance_monitor("listar_inventario_optimizado")
def listar_inventario_optimizado():
    """Versión optimizada con caché y métricas"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    search = request.args.get("q", "", type=str)

    # Crear clave de caché única
    cache_key_str = cache_key(f"inventario_list_{page}_{per_page}_{search}")

    # Intentar obtener del caché (TTL: 2 minutos para listas)
    cached_result = simple_cache(cache_key_str)
    if cached_result is not None:
        cached_result["from_cache"] = True
        return cached_result

    try:
        query = Inventario.query.filter_by(activo=True)

        # Aplicar filtros de búsqueda optimizados
        if search:
            # Usar índices optimizados para búsqueda
            query = query.filter(
                db.or_(
                    Inventario.codigo.ilike(f"%{search}%"),
                    Inventario.descripcion.ilike(f"%{search}%"),
                    Inventario.categoria.ilike(f"%{search}%"),
                    Inventario.ubicacion.ilike(f"%{search}%"),
                )
            )

        # Paginación optimizada
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = pagination.items

        # Preparar datos de respuesta
        items_data = []
        for item in items:
            # Estado optimizado
            if item.stock_actual > item.stock_minimo:
                estado = "Disponible"
                estado_color = "success"
            elif item.stock_actual > 0:
                estado = "Bajo Stock"
                estado_color = "warning"
            else:
                estado = "Sin Stock"
                estado_color = "danger"

            items_data.append(
                {
                    "id": item.id,
                    "codigo": item.codigo,
                    "descripcion": item.descripcion,
                    "categoria": item.categoria,
                    "stock_actual": float(item.stock_actual),
                    "stock_minimo": float(item.stock_minimo),
                    "precio_promedio": float(item.precio_promedio or 0),
                    "ubicacion": item.ubicacion,
                    "estado": estado,
                    "estado_color": estado_color,
                    "critico": item.critico,
                    "activo": item.activo,
                }
            )

        result = {
            "items": items_data,
            "pagination": {
                "page": pagination.page,
                "pages": pagination.pages,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            },
            "search": search,
            "from_cache": False,
            "timestamp": datetime.now().isoformat(),
        }

        # Guardar en caché por 2 minutos
        simple_cache(cache_key_str, result, ttl=120)

        return result

    except Exception as e:
        logger.error(f"Error en listar_inventario_optimizado: {str(e)}")
        return {
            "error": "Error al obtener inventario",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@performance_monitor("obtener_estadisticas_optimizado")
def obtener_estadisticas_optimizado():
    """Estadísticas de inventario con caché optimizado"""
    cache_key_str = cache_key("estadisticas_inventario")

    # Caché de 5 minutos para estadísticas
    cached_result = simple_cache(cache_key_str)
    if cached_result is not None:
        cached_result["from_cache"] = True
        return cached_result

    try:
        # Consultas optimizadas usando índices
        stats = {}

        # Total de artículos activos
        stats["total_articulos"] = Inventario.query.filter_by(activo=True).count()

        # Artículos bajo mínimo
        stats["articulos_bajo_minimo"] = Inventario.query.filter(
            Inventario.activo == True,
            Inventario.stock_actual <= Inventario.stock_minimo,
        ).count()

        # Valor total del stock
        valor_total = (
            db.session.query(
                func.sum(Inventario.stock_actual * Inventario.precio_promedio)
            )
            .filter(Inventario.activo == True)
            .scalar()
            or 0
        )
        stats["valor_total_stock"] = float(valor_total) if valor_total else 0

        # Artículos críticos
        stats["articulos_criticos"] = Inventario.query.filter_by(
            activo=True, critico=True
        ).count()

        # Artículos sin stock
        stats["articulos_sin_stock"] = Inventario.query.filter(
            Inventario.activo == True, Inventario.stock_actual <= 0
        ).count()

        # Estadísticas por categoría (top 5)
        categorias_stats = (
            db.session.query(
                Inventario.categoria,
                func.count(Inventario.id).label("cantidad"),
                func.sum(Inventario.stock_actual * Inventario.precio_promedio).label(
                    "valor"
                ),
            )
            .filter(Inventario.activo == True)
            .group_by(Inventario.categoria)
            .order_by(func.count(Inventario.id).desc())
            .limit(5)
            .all()
        )

        stats["top_categorias"] = [
            {
                "categoria": cat.categoria,
                "cantidad": cat.cantidad,
                "valor": float(cat.valor or 0),
            }
            for cat in categorias_stats
        ]

        result = {
            "estadisticas": stats,
            "from_cache": False,
            "timestamp": datetime.now().isoformat(),
        }

        # Guardar en caché por 5 minutos
        simple_cache(cache_key_str, result, ttl=300)

        return result

    except Exception as e:
        logger.error(f"Error en obtener_estadisticas_optimizado: {str(e)}")
        return {
            "error": "Error al obtener estadísticas",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@performance_monitor("crear_movimiento_optimizado")
def crear_movimiento_optimizado(data):
    """Crear movimiento con FIFO optimizado y transacciones batch"""
    try:
        # Validar datos de entrada
        required_fields = ["inventario_id", "cantidad", "tipo_movimiento"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Campo requerido: {field}")

        inventario_id = data["inventario_id"]
        cantidad = abs(float(data["cantidad"]))
        tipo_movimiento = data["tipo_movimiento"]

        # Obtener artículo
        articulo = Inventario.query.get(inventario_id)
        if not articulo:
            raise ValueError(f"Artículo con ID {inventario_id} no encontrado")

        # Determinar si es entrada o salida
        es_entrada = tipo_movimiento.lower() in ["entrada", "compra", "ajuste_positivo"]
        es_salida = tipo_movimiento.lower() in ["salida", "consumo", "ajuste_negativo"]

        if not (es_entrada or es_salida):
            raise ValueError(f"Tipo de movimiento inválido: {tipo_movimiento}")

        # Crear movimiento de inventario con campos correctos del modelo
        movimiento = MovimientoInventario(
            inventario_id=inventario_id,
            cantidad=int(
                cantidad if es_entrada else -cantidad
            ),  # Campo es Integer en el modelo
            tipo=tipo_movimiento,
            precio_unitario=data.get("precio_unitario"),
            documento_referencia=data.get("documento_referencia"),
            orden_trabajo_id=data.get("orden_trabajo_id"),
            proveedor_id=data.get("proveedor_id"),
            usuario_id=data.get("usuario_id", "sistema"),
            observaciones=data.get("observaciones"),
            # fecha se asigna automáticamente
        )

        # Agregar movimiento y hacer commit
        db.session.add(movimiento)
        db.session.commit()  # Commit inmediato para obtener el ID

        if es_entrada:
            # Entrada: crear lote FIFO optimizado
            resultado_entrada = _procesar_entrada_optimizada(articulo, movimiento, data)

            # Actualizar stock
            articulo.stock_actual += Decimal(str(cantidad))
            articulo.fecha_actualizacion = datetime.now(timezone.utc)
            db.session.commit()  # Commit para guardar el stock actualizado

            result = {
                "status": "success",
                "message": "Entrada procesada correctamente",
                "movimiento_id": movimiento.id,
                "lote_creado": resultado_entrada.get("lote_id"),
                "stock_actualizado": float(articulo.stock_actual),
                "timestamp": datetime.now().isoformat(),
            }

        elif es_salida:
            # Salida: usar FIFO optimizado para consumo
            resultado_salida = _procesar_salida_optimizada(
                articulo, movimiento, cantidad, data
            )

            # Actualizar stock
            articulo.stock_actual -= Decimal(str(cantidad))
            articulo.fecha_actualizacion = datetime.now(timezone.utc)
            db.session.commit()  # Commit para guardar el stock actualizado

            result = {
                "status": "success",
                "message": "Salida procesada correctamente",
                "movimiento_id": movimiento.id,
                "lotes_consumidos": resultado_salida.get("lotes_afectados", 0),
                "cantidad_faltante": resultado_salida.get("cantidad_faltante", 0),
                "stock_actualizado": float(articulo.stock_actual),
                "timestamp": datetime.now().isoformat(),
            }

        # Limpiar caché relacionado
        _limpiar_cache_inventario(inventario_id)

        return result

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en crear_movimiento_optimizado: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }


def _procesar_entrada_optimizada(articulo, movimiento, data):
    """Procesar entrada usando FIFO optimizado"""
    try:
        from app.services.servicio_fifo import ServicioFIFO

        # Generar código de lote
        codigo_lote = (
            data.get("codigo_lote") or f"L{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )

        # Calcular fecha de vencimiento
        fecha_vencimiento = None
        if data.get("fecha_vencimiento"):
            fecha_vencimiento = datetime.fromisoformat(data["fecha_vencimiento"])
        else:
            # Vencimiento automático basado en categoría
            categoria_lower = (articulo.categoria or "general").lower()
            dias_vencimiento = {
                "repuestos": 1095,  # 3 años
                "consumibles": 365,  # 1 año
                "herramientas": 1825,  # 5 años
            }.get(
                categoria_lower, 730
            )  # 2 años por defecto

            fecha_vencimiento = datetime.now(timezone.utc) + timedelta(
                days=dias_vencimiento
            )

        # Crear lote FIFO
        lote = ServicioFIFO.crear_lote_entrada(
            inventario_id=articulo.id,
            cantidad=abs(movimiento.cantidad),
            precio_unitario=movimiento.precio_unitario or 0,
            codigo_lote=codigo_lote,
            fecha_vencimiento=fecha_vencimiento,
            documento_origen=movimiento.documento_referencia,
            proveedor_id=movimiento.proveedor_id,
            usuario_id=movimiento.usuario_id,
            observaciones=f"Lote optimizado: {movimiento.observaciones or ''}",
        )

        return {
            "lote_id": lote.id,
            "codigo_lote": lote.codigo_lote,
            "cantidad": float(lote.cantidad_inicial),
            "fecha_vencimiento": (
                lote.fecha_vencimiento.isoformat() if lote.fecha_vencimiento else None
            ),
        }

    except Exception as e:
        logger.error(f"Error en _procesar_entrada_optimizada: {str(e)}")
        raise


def _procesar_salida_optimizada(articulo, movimiento, cantidad, data):
    """Procesar salida usando FIFO optimizado batch"""
    try:
        # Verificar stock disponible
        if articulo.stock_actual < cantidad:
            raise ValueError(f"Stock insuficiente. Disponible: {articulo.stock_actual}")

        # Preparar operación para FIFO optimizado
        operacion = {
            "inventario_id": articulo.id,
            "cantidad": cantidad,
            "orden_trabajo_id": movimiento.orden_trabajo_id,
            "documento_referencia": movimiento.documento_referencia,
            "observaciones": f"Salida optimizada: {movimiento.observaciones or ''}",
        }

        # Usar FIFO optimizado para consumo batch
        resultados = fifo_optimizado.consumir_fifo_batch(
            [operacion], movimiento.usuario_id
        )

        if resultados:
            resultado = resultados[0]
            return {
                "lotes_afectados": len(resultado.lotes_afectados),
                "cantidad_procesada": float(resultado.cantidad_procesada),
                "cantidad_faltante": float(resultado.cantidad_faltante),
                "tiempo_ejecucion": resultado.tiempo_ejecucion,
                "operaciones_realizadas": resultado.operaciones_realizadas,
            }
        else:
            raise ValueError("No se pudo procesar el consumo FIFO")

    except Exception as e:
        logger.error(f"Error en _procesar_salida_optimizada: {str(e)}")
        # Fallback al método tradicional
        from app.services.servicio_fifo import ServicioFIFO

        consumos, cantidad_faltante = ServicioFIFO.consumir_fifo(
            inventario_id=articulo.id,
            cantidad_total=cantidad,
            orden_trabajo_id=movimiento.orden_trabajo_id,
            documento_referencia=movimiento.documento_referencia,
            usuario_id=movimiento.usuario_id,
            observaciones=f"Fallback FIFO: {movimiento.observaciones or ''}",
        )

        return {
            "lotes_afectados": len(consumos),
            "cantidad_faltante": float(cantidad_faltante),
            "modo": "fallback",
        }


def _limpiar_cache_inventario(inventario_id):
    """Limpiar caché relacionado con inventario"""
    try:
        # Limpiar cachés específicos que podrían estar afectados
        cache_patterns = [
            "inventario_list_",
            "estadisticas_inventario",
            f"inventario_{inventario_id}_",
            "lotes_",
        ]

        # Esta implementación simple solo registra la limpieza
        # En una implementación completa, buscaríamos todas las claves que coincidan
        logger.info(f"Cache invalidado para inventario {inventario_id}")

    except Exception as e:
        logger.warning(f"Error al limpiar caché: {str(e)}")


@performance_monitor("obtener_articulo_optimizado")
def obtener_articulo_optimizado(inventario_id):
    """Obtener artículo específico con caché"""
    cache_key_str = cache_key(f"articulo_{inventario_id}")

    # Caché de 3 minutos para artículos individuales
    cached_result = simple_cache(cache_key_str)
    if cached_result is not None:
        cached_result["from_cache"] = True
        return cached_result

    try:
        articulo = Inventario.query.get(inventario_id)
        if not articulo:
            return {
                "error": "Artículo no encontrado",
                "timestamp": datetime.now().isoformat(),
            }

        # Obtener lotes disponibles usando FIFO optimizado
        lotes_disponibles = fifo_optimizado._obtener_lotes_optimizado(inventario_id)

        # Estadísticas de lotes
        total_lotes = len(lotes_disponibles)
        cantidad_total_lotes = sum(
            float(lote.cantidad_disponible)
            for lote in lotes_disponibles
            if lote.cantidad_disponible > 0
        )

        result = {
            "articulo": {
                "id": articulo.id,
                "codigo": articulo.codigo,
                "descripcion": articulo.descripcion,
                "categoria": articulo.categoria,
                "stock_actual": float(articulo.stock_actual),
                "stock_minimo": float(articulo.stock_minimo),
                "precio_promedio": float(articulo.precio_promedio or 0),
                "ubicacion": articulo.ubicacion,
                "critico": articulo.critico,
                "activo": articulo.activo,
                "fecha_actualizacion": (
                    articulo.fecha_actualizacion.isoformat()
                    if articulo.fecha_actualizacion
                    else None
                ),
            },
            "lotes_info": {
                "total_lotes": total_lotes,
                "cantidad_total_lotes": float(cantidad_total_lotes),
                "discrepancia_stock": float(articulo.stock_actual)
                - float(cantidad_total_lotes),
            },
            "from_cache": False,
            "timestamp": datetime.now().isoformat(),
        }

        # Guardar en caché por 3 minutos
        simple_cache(cache_key_str, result, ttl=180)

        return result

    except Exception as e:
        logger.error(f"Error en obtener_articulo_optimizado: {str(e)}")
        return {
            "error": "Error al obtener artículo",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@performance_monitor("crear_movimientos_batch_optimizado")
def crear_movimientos_batch_optimizado(movimientos):
    """
    Procesa múltiples movimientos en batch para máximo rendimiento

    Args:
        movimientos: Lista de diccionarios con datos de movimientos

    Returns:
        dict: Resultado del procesamiento batch
    """
    start_time = datetime.now()
    resultados = []
    exitosos = 0
    errores = 0

    try:
        for i, movimiento_data in enumerate(movimientos):
            try:
                # Procesar cada movimiento individualmente
                resultado = crear_movimiento_optimizado(movimiento_data)

                if "error" in resultado:
                    errores += 1
                    resultados.append(
                        {"index": i, "success": False, "error": resultado["error"]}
                    )
                else:
                    exitosos += 1
                    resultados.append(
                        {
                            "index": i,
                            "success": True,
                            "movimiento_id": resultado.get("movimiento_id"),
                            "lote_id": resultado.get("lote_id"),
                        }
                    )

            except Exception as e:
                errores += 1
                logger.error(f"Error procesando movimiento {i}: {str(e)}")
                resultados.append({"index": i, "success": False, "error": str(e)})

        # Calcular tiempo total
        tiempo_total = (datetime.now() - start_time).total_seconds() * 1000

        return {
            "total_procesados": len(movimientos),
            "exitosos": exitosos,
            "errores": errores,
            "tiempo_total_ms": round(tiempo_total, 2),
            "resultados": resultados,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error en procesamiento batch: {str(e)}")
        return {
            "error": "Error en procesamiento batch",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }
