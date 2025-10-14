"""
Servicio para gestión FIFO del inventario.
Implementa la lógica de First In, First Out para el control de lotes.
"""

from app.extensions import db
from app.models.inventario import Inventario
from app.models.lote_inventario import LoteInventario, MovimientoLote
from app.models.movimiento_inventario import MovimientoInventario
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ServicioFIFO:
    @staticmethod
    def consumir_fifo(
        inventario_id: int,
        cantidad_total: float,
        orden_trabajo_id: Optional[int] = None,
        documento_referencia: Optional[str] = None,
        usuario_id: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> Tuple[List[Tuple[LoteInventario, float]], float]:
        """
        Consume stock siguiendo FIFO (First In, First Out).

        Args:
            inventario_id: ID del artículo de inventario
            cantidad_total: Cantidad total a consumir
            orden_trabajo_id: ID de la orden de trabajo (opcional)
            documento_referencia: Documento de referencia
            usuario_id: ID del usuario que realiza el consumo
            observaciones: Observaciones adicionales

        Returns:
            Tuple[List[Tuple[LoteInventario, float]], float]:
            Lista de (lote, cantidad_consumida) y cantidad no disponible
        """
        try:
            # Validar que el artículo existe
            inventario = db.session.get(Inventario, inventario_id)
            if not inventario:
                raise ValueError(
                    f"Artículo de inventario {inventario_id} no encontrado"
                )

            # Obtener lotes disponibles ordenados por FIFO
            lotes_consumo, cantidad_faltante = LoteInventario.obtener_lotes_fifo(
                inventario_id, cantidad_total
            )

            if cantidad_faltante > 0:
                logger.warning(
                    f"Stock insuficiente para artículo {inventario_id}: "
                    f"solicitado {cantidad_total}, faltante {cantidad_faltante}"
                )

            # Registrar consumos
            consumos_realizados = []
            for lote, cantidad_a_consumir in lotes_consumo:
                cantidad_consumida = lote.consumir(cantidad_a_consumir)

                if cantidad_consumida > 0:
                    # Registrar el movimiento del lote
                    movimiento_lote = MovimientoLote(
                        lote_id=lote.id,
                        orden_trabajo_id=orden_trabajo_id,
                        tipo_movimiento="consumo",
                        cantidad=Decimal(str(cantidad_consumida)),
                        documento_referencia=documento_referencia,
                        observaciones=observaciones,
                        usuario_id=usuario_id,
                    )
                    db.session.add(movimiento_lote)

                    consumos_realizados.append((lote, cantidad_consumida))

                    logger.info(
                        f"Consumido {cantidad_consumida} del lote {lote.id} "
                        f"(queda {lote.cantidad_actual})"
                    )

            return consumos_realizados, cantidad_faltante

        except Exception as e:
            logger.error(f"Error al consumir FIFO: {str(e)}")
            raise
    """Servicio para gestionar operaciones FIFO en el inventario"""

    @staticmethod
    def crear_lote_entrada(
        inventario_id: int,
        cantidad: float,
        precio_unitario: float,
        codigo_lote: Optional[str] = None,
        fecha_vencimiento: Optional[datetime] = None,
        documento_origen: Optional[str] = None,
        proveedor_id: Optional[int] = None,
        usuario_id: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> LoteInventario:
        """
        Crea un nuevo lote de inventario para una entrada de stock.

        Args:
            inventario_id: ID del artículo de inventario
            cantidad: Cantidad del lote
            precio_unitario: Precio unitario de compra
            codigo_lote: Código opcional del lote
            fecha_vencimiento: Fecha de vencimiento (opcional)
            documento_origen: Documento de origen (factura, orden, etc.)
            proveedor_id: ID del proveedor
            usuario_id: ID del usuario que crea el lote
            observaciones: Observaciones adicionales

        Returns:
            LoteInventario: El lote creado
        """
        try:
            # Validar que el artículo existe
            inventario = db.session.get(Inventario, inventario_id)
            if not inventario:
                raise ValueError(
                    f"Artículo de inventario {inventario_id} no encontrado"
                )

            # Validar cantidad positiva
            if cantidad is None or float(cantidad) <= 0:
                raise ValueError("La cantidad del lote debe ser positiva")

            lote = LoteInventario(
                inventario_id=inventario_id,
                codigo_lote=codigo_lote,
                fecha_vencimiento=fecha_vencimiento,
                cantidad_inicial=Decimal(str(cantidad)),
                cantidad_actual=Decimal(str(cantidad)),
                cantidad_reservada=Decimal("0.0"),
                precio_unitario=Decimal(str(precio_unitario)),
                costo_total=Decimal(str(cantidad)) * Decimal(str(precio_unitario)),
                documento_origen=documento_origen,
                proveedor_id=proveedor_id,
                usuario_creacion=usuario_id,
                observaciones=observaciones,
            )
            db.session.add(lote)
            db.session.commit()
            return lote

        except Exception as e:
            logger.error(f"Error al crear lote: {str(e)}")
            raise
            inventario = db.session.get(Inventario, inventario_id)
            if not inventario:
                raise ValueError(
                    f"Artículo de inventario {inventario_id} no encontrado"
                )

            # Obtener lotes disponibles ordenados por FIFO
            lotes_consumo, cantidad_faltante = LoteInventario.obtener_lotes_fifo(
                inventario_id, cantidad_total
            )

            if cantidad_faltante > 0:
                logger.warning(
                    f"Stock insuficiente para artículo {inventario_id}: "
                    f"solicitado {cantidad_total}, faltante {cantidad_faltante}"
                )

            # Registrar consumos
            consumos_realizados = []
            for lote, cantidad_a_consumir in lotes_consumo:
                cantidad_consumida = lote.consumir(cantidad_a_consumir)

                if cantidad_consumida > 0:
                    # Registrar el movimiento del lote
                    movimiento_lote = MovimientoLote(
                        lote_id=lote.id,
                        orden_trabajo_id=orden_trabajo_id,
                        tipo_movimiento="consumo",
                        cantidad=Decimal(str(cantidad_consumida)),
                        documento_referencia=documento_referencia,
                        observaciones=observaciones,
                        usuario_id=usuario_id,
                    )
                    db.session.add(movimiento_lote)

                    consumos_realizados.append((lote, cantidad_consumida))

                    logger.info(
                        f"Consumido {cantidad_consumida} del lote {lote.id} "
                        f"(queda {lote.cantidad_actual})"
                    )

            return consumos_realizados, cantidad_faltante

        except Exception as e:
            logger.error(f"Error al consumir FIFO: {str(e)}")
            raise

    @staticmethod
    def reservar_stock(
        inventario_id: int,
        cantidad_total: float,
        orden_trabajo_id: Optional[int] = None,
        documento_referencia: Optional[str] = None,
        usuario_id: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> Tuple[List[Tuple[LoteInventario, float]], float]:
        """
        Reserva stock siguiendo FIFO sin consumirlo inmediatamente.

        Args:
            inventario_id: ID del artículo de inventario
            cantidad_total: Cantidad total a reservar
            orden_trabajo_id: ID de la orden de trabajo
            documento_referencia: Documento de referencia
            usuario_id: ID del usuario que realiza la reserva
            observaciones: Observaciones adicionales

        Returns:
            Tuple[List[Tuple[LoteInventario, float]], float]:
            Lista de (lote, cantidad_reservada) y cantidad no disponible
        """
        try:
            # Obtener lotes disponibles ordenados por FIFO
            lotes_reserva, cantidad_faltante = LoteInventario.obtener_lotes_fifo(
                inventario_id, cantidad_total
            )

            # Registrar reservas
            reservas_realizadas = []
            for lote, cantidad_a_reservar in lotes_reserva:
                cantidad_reservada = lote.reservar(cantidad_a_reservar)

                if cantidad_reservada > 0:
                    # Registrar el movimiento del lote
                    movimiento_lote = MovimientoLote(
                        lote_id=lote.id,
                        orden_trabajo_id=orden_trabajo_id,
                        tipo_movimiento="reserva",
                        cantidad=Decimal(str(cantidad_reservada)),
                        documento_referencia=documento_referencia,
                        observaciones=observaciones,
                        usuario_id=usuario_id,
                    )
                    db.session.add(movimiento_lote)

                    reservas_realizadas.append((lote, cantidad_reservada))

                    logger.info(
                        f"Reservado {cantidad_reservada} del lote {lote.id} "
                        f"(disponible {lote.cantidad_disponible})"
                    )

            return reservas_realizadas, cantidad_faltante

        except Exception as e:
            logger.error(f"Error al reservar stock: {str(e)}")
            raise

    @staticmethod
    def liberar_reservas(
        orden_trabajo_id: int,
        usuario_id: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> List[Tuple[LoteInventario, float]]:
        """
        Libera todas las reservas de una orden de trabajo.

        Args:
            orden_trabajo_id: ID de la orden de trabajo
            usuario_id: ID del usuario que libera las reservas
            observaciones: Observaciones adicionales

        Returns:
            List[Tuple[LoteInventario, float]]: Lista de (lote, cantidad_liberada)
        """
        try:
            # Buscar movimientos de reserva pendientes
            movimientos_reserva = MovimientoLote.query.filter_by(
                orden_trabajo_id=orden_trabajo_id, tipo_movimiento="reserva"
            ).all()

            liberaciones_realizadas = []

            for movimiento in movimientos_reserva:
                lote = movimiento.lote
                cantidad_liberada = lote.liberar_reserva(float(movimiento.cantidad))

                if cantidad_liberada > 0:
                    # Registrar la liberación
                    movimiento_liberacion = MovimientoLote(
                        lote_id=lote.id,
                        orden_trabajo_id=orden_trabajo_id,
                        tipo_movimiento="liberacion",
                        cantidad=Decimal(str(cantidad_liberada)),
                        observaciones=observaciones,
                        usuario_id=usuario_id,
                    )
                    db.session.add(movimiento_liberacion)

                    liberaciones_realizadas.append((lote, cantidad_liberada))

                    logger.info(
                        f"Liberado {cantidad_liberada} del lote {lote.id} "
                        f"para orden {orden_trabajo_id}"
                    )

            return liberaciones_realizadas

        except Exception as e:
            logger.error(f"Error al liberar reservas: {str(e)}")
            raise

    @staticmethod
    def obtener_stock_disponible(inventario_id: int) -> dict:
        """
        Obtiene información detallada del stock disponible por lotes.

        Args:
            inventario_id: ID del artículo de inventario

        Returns:
            dict: Información detallada del stock
        """
        try:
            lotes = (
                LoteInventario.query.filter_by(inventario_id=inventario_id, activo=True)
                .filter(LoteInventario.cantidad_actual > 0)
                .order_by(LoteInventario.fecha_entrada.asc())
                .all()
            )

            total_actual = sum(float(lote.cantidad_actual) for lote in lotes)
            total_reservado = sum(float(lote.cantidad_reservada) for lote in lotes)
            total_disponible = total_actual - total_reservado

            lotes_info = []
            for lote in lotes:
                lotes_info.append(
                    {
                        "id": lote.id,
                        "codigo_lote": lote.codigo_lote,
                        "fecha_entrada": lote.fecha_entrada.isoformat(),
                        "cantidad_actual": float(lote.cantidad_actual),
                        "cantidad_reservada": float(lote.cantidad_reservada),
                        "cantidad_disponible": lote.cantidad_disponible,
                        "precio_unitario": float(lote.precio_unitario),
                        "fecha_vencimiento": (
                            lote.fecha_vencimiento.isoformat()
                            if lote.fecha_vencimiento
                            else None
                        ),
                        "esta_vencido": lote.esta_vencido,
                        "dias_hasta_vencimiento": lote.dias_hasta_vencimiento,
                    }
                )

            return {
                "inventario_id": inventario_id,
                "total_actual": total_actual,
                "total_reservado": total_reservado,
                "total_disponible": total_disponible,
                "numero_lotes": len(lotes),
                "lotes": lotes_info,
            }

        except Exception as e:
            logger.error(f"Error al obtener stock disponible: {str(e)}")
            raise

    @staticmethod
    def integrar_con_movimiento_inventario(
        movimiento: MovimientoInventario, usuario_id: Optional[str] = None
    ) -> Optional[LoteInventario]:
        """
        Integra un movimiento de inventario tradicional con el sistema de lotes.

        Args:
            movimiento: MovimientoInventario a integrar
            usuario_id: ID del usuario que realiza la integración

        Returns:
            LoteInventario: El lote creado (solo para entradas) o None
        """
        try:
            if movimiento.es_entrada:
                # Crear nuevo lote para entradas
                lote = ServicioFIFO.crear_lote_entrada(
                    inventario_id=movimiento.inventario_id,
                    cantidad=abs(movimiento.cantidad),
                    precio_unitario=movimiento.precio_unitario or 0,
                    documento_origen=movimiento.documento_referencia,
                    proveedor_id=movimiento.proveedor_id,
                    usuario_id=usuario_id or movimiento.usuario_id,
                    observaciones=movimiento.observaciones,
                )

                # Vincular el lote con el movimiento
                lote.movimiento_entrada_id = movimiento.id
                db.session.flush()

                logger.info(
                    f"Lote {lote.id} creado para movimiento de entrada {movimiento.id}"
                )
                return lote

            elif movimiento.es_salida:
                # Consumir stock usando FIFO para salidas
                consumos, faltante = ServicioFIFO.consumir_fifo(
                    inventario_id=movimiento.inventario_id,
                    cantidad_total=abs(movimiento.cantidad),
                    orden_trabajo_id=movimiento.orden_trabajo_id,
                    documento_referencia=movimiento.documento_referencia,
                    usuario_id=usuario_id or movimiento.usuario_id,
                    observaciones=movimiento.observaciones,
                )

                if faltante > 0:
                    logger.warning(
                        f"Movimiento {movimiento.id}: stock insuficiente, "
                        f"faltante {faltante}"
                    )

                logger.info(f"Consumo FIFO realizado para movimiento {movimiento.id}")
                return None

        except Exception as e:
            logger.error(f"Error al integrar movimiento {movimiento.id}: {str(e)}")
            raise
