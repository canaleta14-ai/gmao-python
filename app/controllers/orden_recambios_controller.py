from app.models import OrdenRecambio, OrdenTrabajo, Inventario, MovimientoInventario
from app.extensions import db
from datetime import datetime, timezone


def agregar_recambio_a_orden(
    orden_id, inventario_id, cantidad_solicitada, observaciones=None
):
    """Agregar un recambio/repuesto a una orden de trabajo"""
    try:
        # Validar que la orden existe
        orden = OrdenTrabajo.query.get(orden_id)
        if not orden:
            raise ValueError("Orden de trabajo no encontrada")

        # Validar que el artículo existe
        articulo = Inventario.query.get(inventario_id)
        if not articulo:
            raise ValueError("Artículo de inventario no encontrado")

        # Verificar si ya existe este recambio en la orden
        recambio_existente = OrdenRecambio.query.filter_by(
            orden_trabajo_id=orden_id, inventario_id=inventario_id
        ).first()

        if recambio_existente:
            # Actualizar cantidad si ya existe
            recambio_existente.cantidad_solicitada += cantidad_solicitada
            if observaciones:
                recambio_existente.observaciones = (
                    recambio_existente.observaciones or ""
                ) + f"\n{observaciones}"
        else:
            # Crear nuevo recambio
            recambio = OrdenRecambio(
                orden_trabajo_id=orden_id,
                inventario_id=inventario_id,
                cantidad_solicitada=cantidad_solicitada,
                precio_unitario=articulo.precio_promedio,
                observaciones=observaciones,
            )
            db.session.add(recambio)

        db.session.commit()

        return recambio_existente if recambio_existente else recambio

    except Exception as e:
        db.session.rollback()
        raise e


def obtener_recambios_orden(orden_id):
    """Obtener todos los recambios de una orden de trabajo"""
    recambios = OrdenRecambio.query.filter_by(orden_trabajo_id=orden_id).all()
    return [recambio.to_dict() for recambio in recambios]


def descontar_recambios_orden(orden_id, usuario_id="sistema", es_automatico=False):
    """Descontar del stock todos los recambios utilizados en una orden"""
    try:
        # Validar que la orden existe y obtener su estado
        orden = OrdenTrabajo.query.get(orden_id)
        if not orden:
            raise ValueError("Orden de trabajo no encontrada")
        
        # Validar que la orden no esté cerrada para descuentos manuales
        if not es_automatico and orden.estado in ["Completada", "Cancelada"]:
            raise ValueError(
                f"No se pueden descontar repuestos de una orden {orden.estado.lower()}. "
                f"La orden debe estar en estado 'En Proceso', 'Pendiente' o 'En Espera'."
            )
        
        # Obtener todos los recambios no descontados de la orden
        recambios = OrdenRecambio.query.filter_by(
            orden_trabajo_id=orden_id, descontado=False
        ).all()

        if not recambios:
            mensaje = (
                "No hay recambios pendientes para descontar"
                if es_automatico
                else "No hay recambios para descontar"
            )
            return {
                "mensaje": mensaje,
                "recambios_descontados": [],
            }

        recambios_descontados = []
        errores = []

        for recambio in recambios:
            try:
                articulo = recambio.inventario
                cantidad_a_descontar = (
                    recambio.cantidad_utilizada or recambio.cantidad_solicitada
                )

                # Verificar stock disponible
                if articulo.stock_actual < cantidad_a_descontar:
                    errores.append(
                        {
                            "articulo": articulo.codigo,
                            "error": f"Stock insuficiente. Disponible: {articulo.stock_actual}, Requerido: {cantidad_a_descontar}",
                        }
                    )
                    continue

                # Descontar del stock
                articulo.stock_actual -= cantidad_a_descontar

                # Crear movimiento de inventario
                movimiento = MovimientoInventario(
                    inventario_id=articulo.id,
                    tipo="salida",
                    subtipo="orden_trabajo",
                    cantidad=cantidad_a_descontar,
                    precio_unitario=recambio.precio_unitario,
                    valor_total=(recambio.precio_unitario or 0) * cantidad_a_descontar,
                    documento_referencia=f"OT-{orden_id}",
                    observaciones=f"Recambio utilizado en orden {orden_id}: {recambio.observaciones or ''}",
                    usuario_id=usuario_id,
                )

                # Marcar recambio como descontado
                recambio.descontado = True
                recambio.fecha_descuento = datetime.now(timezone.utc)
                recambio.cantidad_utilizada = cantidad_a_descontar

                db.session.add(movimiento)

                recambios_descontados.append(
                    {
                        "articulo": articulo.codigo,
                        "descripcion": articulo.descripcion,
                        "cantidad": cantidad_a_descontar,
                        "stock_anterior": articulo.stock_actual + cantidad_a_descontar,
                        "stock_actual": articulo.stock_actual,
                    }
                )

            except Exception as e:
                errores.append(
                    {
                        "articulo": (
                            recambio.inventario.codigo if recambio.inventario else "N/A"
                        ),
                        "error": str(e),
                    }
                )

        db.session.commit()

        # Mensajes diferenciados según el tipo de descuento
        if es_automatico:
            mensaje = (
                f"Descuento automático completado: {len(recambios_descontados)} recambios"
                if recambios_descontados
                else "Descuento automático: sin recambios pendientes"
            )
        else:
            mensaje = f"Proceso completado. {len(recambios_descontados)} recambios descontados"

        return {
            "mensaje": mensaje,
            "recambios_descontados": recambios_descontados,
            "errores": errores,
        }

    except Exception as e:
        db.session.rollback()
        raise e


def actualizar_cantidad_utilizada(recambio_id, cantidad_utilizada):
    """Actualizar la cantidad realmente utilizada de un recambio"""
    try:
        recambio = OrdenRecambio.query.get(recambio_id)
        if not recambio:
            raise ValueError("Recambio no encontrado")

        if recambio.descontado:
            raise ValueError(
                "No se puede modificar un recambio ya descontado del stock"
            )

        recambio.cantidad_utilizada = cantidad_utilizada
        db.session.commit()

        return recambio.to_dict()

    except Exception as e:
        db.session.rollback()
        raise e


def eliminar_recambio(recambio_id):
    """Eliminar un recambio de una orden (solo si no ha sido descontado)"""
    try:
        recambio = OrdenRecambio.query.get(recambio_id)
        if not recambio:
            raise ValueError("Recambio no encontrado")

        if recambio.descontado:
            raise ValueError("No se puede eliminar un recambio ya descontado del stock")

        db.session.delete(recambio)
        db.session.commit()

        return {"mensaje": "Recambio eliminado exitosamente"}

    except Exception as e:
        db.session.rollback()
        raise e
