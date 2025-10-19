"""
Blueprint para gestión de lotes FIFO
Interfaz web para visualizar, crear y gestionar lotes de inventario
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Inventario
from app.models.lote_inventario import LoteInventario, MovimientoLote
from app.services.servicio_fifo import ServicioFIFO
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# Blueprint para gestión de lotes
lotes_bp = Blueprint("lotes", __name__, url_prefix="/lotes")


@lotes_bp.route("/")
@login_required
def index():
    """Página principal de gestión de lotes"""
    return render_template("lotes/index.html")


@lotes_bp.route("/demo")
def demo():
    """Página de demostración sin autenticación"""
    try:
        # Obtener artículos de prueba
        articulos = (
            Inventario.query.filter(Inventario.codigo.like("FIFO-%"))
            .order_by(Inventario.codigo)
            .all()
        )

        # Obtener lotes de los artículos de prueba
        from app.models.lote_inventario import LoteInventario

        lotes = (
            LoteInventario.query.join(Inventario)
            .filter(Inventario.codigo.like("FIFO-%"))
            .order_by(LoteInventario.fecha_entrada.desc())
            .all()
        )

        return render_template("lotes/demo.html", articulos=articulos, lotes=lotes)

    except Exception as e:
        logger.error(f"Error en demo: {str(e)}")
        return f"Error: {str(e)}", 500


@lotes_bp.route("/inventario/<int:inventario_id>")
@login_required
def detalle_inventario(inventario_id):
    """Detalle de lotes de un artículo específico"""
    try:
        inventario = Inventario.query.get_or_404(inventario_id)

        # Obtener información detallada de stock
        stock_info = ServicioFIFO.obtener_stock_disponible(inventario_id)

        # Obtener historial de movimientos recientes
        movimientos = (
            MovimientoLote.query.join(LoteInventario)
            .filter(LoteInventario.inventario_id == inventario_id)
            .order_by(MovimientoLote.fecha.desc())
            .limit(50)
            .all()
        )

        return render_template(
            "lotes/detalle_inventario.html",
            inventario=inventario,
            stock_info=stock_info,
            movimientos=movimientos,
        )

    except Exception as e:
        logger.error(
            f"Error al obtener detalle de inventario {inventario_id}: {str(e)}"
        )
        flash(f"Error al cargar información del artículo: {str(e)}", "error")
        return redirect(url_for("lotes.index"))


@lotes_bp.route("/crear_lote", methods=["GET", "POST"])
@login_required
def crear_lote():
    """Crear un nuevo lote de inventario"""
    if request.method == "GET":
        # Obtener lista de artículos para el formulario
        articulos = (
            Inventario.query.filter_by(activo=True).order_by(Inventario.codigo).all()
        )
        return render_template("lotes/crear_lote.html", articulos=articulos)

    try:
        # Procesar formulario
        inventario_id = int(request.form["inventario_id"])
        cantidad = float(request.form["cantidad"])
        precio_unitario = float(request.form["precio_unitario"])
        codigo_lote = request.form.get("codigo_lote", "").strip() or None
        documento_origen = request.form.get("documento_origen", "").strip() or None
        observaciones = request.form.get("observaciones", "").strip() or None

        # Fecha de vencimiento opcional
        fecha_vencimiento = None
        if request.form.get("fecha_vencimiento"):
            fecha_vencimiento = datetime.strptime(
                request.form["fecha_vencimiento"], "%Y-%m-%d"
            ).replace(tzinfo=timezone.utc)

        # Validaciones
        if cantidad <= 0:
            flash("La cantidad debe ser mayor a cero", "error")
            return redirect(url_for("lotes.crear_lote"))

        if precio_unitario < 0:
            flash("El precio unitario no puede ser negativo", "error")
            return redirect(url_for("lotes.crear_lote"))

        # Crear el lote usando el servicio FIFO
        lote = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_id,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            codigo_lote=codigo_lote,
            fecha_vencimiento=fecha_vencimiento,
            documento_origen=documento_origen,
            usuario_id=current_user.username,
            observaciones=observaciones,
        )

        db.session.commit()

        flash(f"Lote creado exitosamente: {lote.codigo_lote or lote.id}", "success")
        return redirect(
            url_for("lotes.detalle_inventario", inventario_id=inventario_id)
        )

    except ValueError as e:
        flash(f"Error en los datos proporcionados: {str(e)}", "error")
        return redirect(url_for("lotes.crear_lote"))
    except Exception as e:
        logger.error(f"Error al crear lote: {str(e)}")
        flash(f"Error al crear el lote: {str(e)}", "error")
        db.session.rollback()
        return redirect(url_for("lotes.crear_lote"))


@lotes_bp.route("/api/articulos")
def api_articulos():
    """API pública para obtener artículos disponibles (para autocompletado)"""
    try:
        articulos = (
            Inventario.query.filter_by(activo=True).order_by(Inventario.codigo).all()
        )

        articulos_data = []
        for articulo in articulos:
            articulos_data.append(
                {
                    "id": articulo.id,
                    "codigo": articulo.codigo,
                    "nombre": articulo.nombre or "",
                    "unidad_medida": articulo.unidad_medida or "UN",
                    "stock_actual": float(articulo.stock_actual or 0),
                }
            )

        return jsonify({"success": True, "articulos": articulos_data})

    except Exception as e:
        logger.error(f"Error al obtener artículos: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@lotes_bp.route("/api/inventario/activos")
def api_inventario_activos():
    """API pública para obtener inventario activo"""
    try:
        articulos = Inventario.query.filter_by(activo=True).all()
        return jsonify(
            {
                "success": True,
                "count": len(articulos),
                "articulos": [
                    {"id": a.id, "codigo": a.codigo, "nombre": a.nombre}
                    for a in articulos
                ],
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@lotes_bp.route("/api/lotes/activos")
@login_required
def api_lotes_activos():
    """API para obtener todos los lotes activos con paginación y filtros"""
    try:
        # Parámetros de paginación
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        # Parámetros de filtros
        inventario_id = request.args.get("inventario_id", type=int)
        codigo_lote = request.args.get("codigo_lote", type=str)
        fecha_entrada_desde = request.args.get("fecha_entrada_desde", type=str)
        fecha_entrada_hasta = request.args.get("fecha_entrada_hasta", type=str)
        fecha_vencimiento_desde = request.args.get("fecha_vencimiento_desde", type=str)
        fecha_vencimiento_hasta = request.args.get("fecha_vencimiento_hasta", type=str)

        # Parámetros de ordenamiento
        sort_by = request.args.get("sort_by", "fecha_entrada")
        sort_order = request.args.get("sort_order", "desc")

        # Query base: lotes con cantidad disponible > 0
        query = LoteInventario.query.filter(
            LoteInventario.cantidad_actual > LoteInventario.cantidad_reservada
        )

        # Aplicar filtros
        if inventario_id:
            query = query.filter(LoteInventario.inventario_id == inventario_id)

        if codigo_lote:
            query = query.filter(LoteInventario.codigo_lote.ilike(f"%{codigo_lote}%"))

        if fecha_entrada_desde:
            from datetime import datetime

            fecha_desde = datetime.fromisoformat(fecha_entrada_desde)
            query = query.filter(LoteInventario.fecha_entrada >= fecha_desde)

        if fecha_entrada_hasta:
            from datetime import datetime

            fecha_hasta = datetime.fromisoformat(fecha_entrada_hasta)
            query = query.filter(LoteInventario.fecha_entrada <= fecha_hasta)

        if fecha_vencimiento_desde:
            from datetime import datetime

            fecha_desde = datetime.fromisoformat(fecha_vencimiento_desde)
            query = query.filter(LoteInventario.fecha_vencimiento >= fecha_desde)

        if fecha_vencimiento_hasta:
            from datetime import datetime

            fecha_hasta = datetime.fromisoformat(fecha_vencimiento_hasta)
            query = query.filter(LoteInventario.fecha_vencimiento <= fecha_hasta)

        # Aplicar ordenamiento
        if sort_by == "codigo_lote":
            order_col = LoteInventario.codigo_lote
        elif sort_by == "cantidad_disponible":
            order_col = (
                LoteInventario.cantidad_actual
            )  # No se puede ordenar por property
        elif sort_by == "fecha_vencimiento":
            order_col = LoteInventario.fecha_vencimiento
        else:  # fecha_entrada por defecto
            order_col = LoteInventario.fecha_entrada

        if sort_order == "asc":
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())

        # Ejecutar paginación
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        lotes_data = []
        for lote in pagination.items:
            lotes_data.append(
                {
                    "id": lote.id,
                    "codigo_lote": lote.codigo_lote,
                    "inventario_id": lote.inventario_id,
                    "inventario_codigo": (
                        lote.inventario.codigo if lote.inventario else None
                    ),
                    "inventario_nombre": (
                        lote.inventario.nombre if lote.inventario else None
                    ),
                    "cantidad_inicial": float(lote.cantidad_inicial),
                    "cantidad_disponible": float(lote.cantidad_disponible),
                    "cantidad_reservada": float(lote.cantidad_reservada),
                    "fecha_entrada": (
                        lote.fecha_entrada.isoformat() if lote.fecha_entrada else None
                    ),
                    "fecha_vencimiento": (
                        lote.fecha_vencimiento.isoformat()
                        if lote.fecha_vencimiento
                        else None
                    ),
                    "proveedor_id": lote.proveedor_id,
                    "documento_origen": lote.documento_origen,
                    "precio_unitario": (
                        float(lote.precio_unitario) if lote.precio_unitario else None
                    ),
                    "activo": lote.activo,
                }
            )

        # Retornar datos con información de paginación
        return jsonify(
            {
                "success": True,
                "lotes": lotes_data,
                "pagination": {
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "current_page": pagination.page,
                    "per_page": pagination.per_page,
                    "has_next": pagination.has_next,
                    "has_prev": pagination.has_prev,
                    "next_page": pagination.next_num if pagination.has_next else None,
                    "prev_page": pagination.prev_num if pagination.has_prev else None,
                },
            }
        )
    except Exception as e:
        logger.error(f"Error al obtener lotes activos: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@lotes_bp.route("/api/lotes/<int:inventario_id>")
@login_required
def api_lotes_inventario(inventario_id):
    """API para obtener lotes de un artículo (AJAX)"""
    try:
        stock_info = ServicioFIFO.obtener_stock_disponible(inventario_id)
        return jsonify({"success": True, "stock_info": stock_info})
    except Exception as e:
        logger.error(f"Error en API lotes: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@lotes_bp.route("/api/lote/<int:lote_id>")
@login_required
def api_lote_individual(lote_id):
    """API para obtener información de un lote individual"""
    try:
        lote = LoteInventario.query.get_or_404(lote_id)

        # Calcular días hasta vencimiento
        dias_hasta_vencimiento = None
        estado_vencimiento = "normal"
        if lote.fecha_vencimiento:
            delta = (
                lote.fecha_vencimiento.replace(tzinfo=timezone.utc)
                - datetime.now(timezone.utc)
            ).days
            dias_hasta_vencimiento = delta

            if delta < 0:
                estado_vencimiento = "vencido"
            elif delta <= 7:
                estado_vencimiento = "critico"
            elif delta <= 30:
                estado_vencimiento = "proximo"

        lote_data = {
            "id": lote.id,
            "codigo_lote": lote.codigo_lote or f"Lote-{lote.id}",
            "inventario_id": lote.inventario_id,
            "inventario_codigo": lote.inventario.codigo,
            "inventario_nombre": lote.inventario.nombre,
            "cantidad_inicial": float(lote.cantidad_inicial),
            "cantidad_actual": float(lote.cantidad_actual),
            "cantidad_reservada": float(lote.cantidad_reservada or 0),
            "unidad_medida": lote.inventario.unidad_medida or "UN",
            "precio_unitario": float(lote.precio_unitario or 0),
            "valor_total": float(lote.cantidad_actual * (lote.precio_unitario or 0)),
            "fecha_entrada": (
                lote.fecha_entrada.isoformat() if lote.fecha_entrada else None
            ),
            "fecha_vencimiento": (
                lote.fecha_vencimiento.isoformat() if lote.fecha_vencimiento else None
            ),
            "dias_hasta_vencimiento": dias_hasta_vencimiento,
            "estado_vencimiento": estado_vencimiento,
            "documento_origen": lote.documento_origen,
            "proveedor": lote.proveedor,
            "observaciones": lote.observaciones,
            "ubicacion": lote.ubicacion,
            "activo": lote.activo,
        }

        return jsonify({"success": True, "lote": lote_data})

    except Exception as e:
        logger.error(f"Error al obtener lote {lote_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@lotes_bp.route("/api/consumir", methods=["POST"])
@login_required
def api_consumir_fifo():
    """API para consumir stock usando FIFO"""
    try:
        data = request.get_json()

        # Validar que se recibió JSON
        if not data:
            return jsonify({"success": False, "error": "No se recibieron datos"}), 400

        # Validar campos requeridos
        if "inventario_id" not in data:
            return (
                jsonify({"success": False, "error": "inventario_id es requerido"}),
                400,
            )
        if "cantidad" not in data:
            return jsonify({"success": False, "error": "cantidad es requerida"}), 400

        inventario_id = int(data["inventario_id"])
        cantidad = float(data["cantidad"])
        orden_trabajo_id = data.get("orden_trabajo_id")
        documento_referencia = data.get("documento_referencia", "")
        observaciones = data.get("observaciones", "")

        # Validaciones
        if cantidad <= 0:
            return (
                jsonify(
                    {"success": False, "error": "La cantidad debe ser mayor a cero"}
                ),
                400,
            )

        # Consumir usando FIFO
        consumos, faltante = ServicioFIFO.consumir_fifo(
            inventario_id=inventario_id,
            cantidad_total=cantidad,
            orden_trabajo_id=orden_trabajo_id,
            documento_referencia=documento_referencia,
            usuario_id=current_user.username,
            observaciones=observaciones,
        )

        db.session.commit()

        # Preparar respuesta
        consumos_data = []
        for lote, cantidad_consumida in consumos:
            consumos_data.append(
                {
                    "lote_id": lote.id,
                    "codigo_lote": lote.codigo_lote or f"Lote-{lote.id}",
                    "cantidad_consumida": cantidad_consumida,
                }
            )

        return jsonify(
            {
                "success": True,
                "consumos": consumos_data,
                "cantidad_faltante": faltante,
                "total_consumido": sum(c[1] for c in consumos),
            }
        )

    except (ValueError, TypeError) as e:
        db.session.rollback()
        return (
            jsonify({"success": False, "error": f"Error en los datos: {str(e)}"}),
            400,
        )
    except Exception as e:
        logger.error(f"Error al consumir FIFO: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@lotes_bp.route("/api/lote/<int:lote_id>/priorizar", methods=["POST"])
@login_required
def api_priorizar_lote(lote_id):
    """API para marcar un lote como prioritario en el consumo FIFO"""
    try:
        data = request.get_json() or {}

        lote = LoteInventario.query.get_or_404(lote_id)

        # Verificar que el lote está activo y tiene cantidad disponible
        if not lote.activo:
            return jsonify({"success": False, "error": "El lote no está activo"}), 400

        if lote.cantidad_actual <= 0:
            return (
                jsonify(
                    {"success": False, "error": "El lote no tiene stock disponible"}
                ),
                400,
            )

        # Obtener la fecha de entrada más antigua del mismo artículo
        lote_mas_antiguo = (
            LoteInventario.query.filter_by(
                inventario_id=lote.inventario_id, activo=True
            )
            .filter(LoteInventario.cantidad_actual > 0)
            .order_by(LoteInventario.fecha_entrada.asc())
            .first()
        )

        if not lote_mas_antiguo:
            return jsonify({"success": False, "error": "No hay lotes disponibles"}), 400

        # Ajustar la fecha de entrada para que sea anterior al más antiguo
        # Restar 1 día a la fecha más antigua
        nueva_fecha = lote_mas_antiguo.fecha_entrada - timedelta(days=1)

        fecha_original = lote.fecha_entrada
        lote.fecha_entrada = nueva_fecha

        # Registrar el cambio en observaciones
        observacion_prioridad = data.get("observaciones", "Lote priorizado manualmente")
        if lote.observaciones:
            lote.observaciones += f"\n[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}] PRIORIZADO: {observacion_prioridad}"
        else:
            lote.observaciones = f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}] PRIORIZADO: {observacion_prioridad}"

        # Registrar movimiento de ajuste
        movimiento = MovimientoLote(
            lote_id=lote.id,
            tipo_movimiento="ajuste_prioridad",
            cantidad=0,  # Sin cambio de cantidad
            cantidad_anterior=lote.cantidad_actual,
            cantidad_nueva=lote.cantidad_actual,
            documento_referencia=f"Priorización de lote - Fecha original: {fecha_original.strftime('%Y-%m-%d')}",
            observaciones=observacion_prioridad,
            usuario_id=current_user.username,
            fecha=datetime.now(timezone.utc),
        )

        db.session.add(movimiento)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Lote priorizado exitosamente",
                "lote": {
                    "id": lote.id,
                    "codigo_lote": lote.codigo_lote or f"Lote-{lote.id}",
                    "fecha_entrada_original": fecha_original.isoformat(),
                    "fecha_entrada_nueva": nueva_fecha.isoformat(),
                    "inventario_codigo": lote.inventario.codigo,
                    "inventario_nombre": lote.inventario.nombre,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error al priorizar lote {lote_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@lotes_bp.route("/api/lote/<int:lote_id>/mover", methods=["POST"])
@login_required
def api_mover_lote(lote_id):
    """API para mover un lote a otra ubicación/almacén"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No se recibieron datos"}), 400

        # Validar campos requeridos
        if "ubicacion" not in data:
            return (
                jsonify({"success": False, "error": "La ubicación es requerida"}),
                400,
            )

        lote = LoteInventario.query.get_or_404(lote_id)

        # Verificar que el lote está activo
        if not lote.activo:
            return jsonify({"success": False, "error": "El lote no está activo"}), 400

        ubicacion_original = lote.ubicacion or "Sin ubicación"
        nueva_ubicacion = data["ubicacion"].strip()

        if not nueva_ubicacion:
            return (
                jsonify(
                    {"success": False, "error": "La ubicación no puede estar vacía"}
                ),
                400,
            )

        if ubicacion_original == nueva_ubicacion:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "La nueva ubicación es igual a la actual",
                    }
                ),
                400,
            )

        # Actualizar ubicación
        lote.ubicacion = nueva_ubicacion

        # Registrar en observaciones
        observacion_movimiento = data.get(
            "observaciones", f"Movido de '{ubicacion_original}' a '{nueva_ubicacion}'"
        )
        if lote.observaciones:
            lote.observaciones += f"\n[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}] MOVIMIENTO: {observacion_movimiento}"
        else:
            lote.observaciones = f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}] MOVIMIENTO: {observacion_movimiento}"

        # Registrar movimiento
        movimiento = MovimientoLote(
            lote_id=lote.id,
            tipo_movimiento="movimiento_ubicacion",
            cantidad=0,  # Sin cambio de cantidad
            cantidad_anterior=lote.cantidad_actual,
            cantidad_nueva=lote.cantidad_actual,
            documento_referencia=f"Movimiento: {ubicacion_original} → {nueva_ubicacion}",
            observaciones=observacion_movimiento,
            usuario_id=current_user.username,
            fecha=datetime.now(timezone.utc),
        )

        db.session.add(movimiento)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Lote movido exitosamente de '{ubicacion_original}' a '{nueva_ubicacion}'",
                "lote": {
                    "id": lote.id,
                    "codigo_lote": lote.codigo_lote or f"Lote-{lote.id}",
                    "ubicacion_original": ubicacion_original,
                    "ubicacion_nueva": nueva_ubicacion,
                    "inventario_codigo": lote.inventario.codigo,
                    "inventario_nombre": lote.inventario.nombre,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error al mover lote {lote_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@lotes_bp.route("/api/reservar", methods=["POST"])
@login_required
def api_reservar_stock():
    """API para reservar stock usando FIFO"""
    try:
        data = request.get_json()

        # Validar que se recibió JSON
        if not data:
            return jsonify({"success": False, "error": "No se recibieron datos"}), 400

        # Validar campos requeridos
        if "inventario_id" not in data:
            return (
                jsonify({"success": False, "error": "inventario_id es requerido"}),
                400,
            )
        if "cantidad" not in data:
            return jsonify({"success": False, "error": "cantidad es requerida"}), 400
        if "orden_trabajo_id" not in data:
            return (
                jsonify({"success": False, "error": "orden_trabajo_id es requerido"}),
                400,
            )

        inventario_id = int(data["inventario_id"])
        cantidad = float(data["cantidad"])
        orden_trabajo_id = int(data["orden_trabajo_id"])
        documento_referencia = data.get("documento_referencia", "")
        observaciones = data.get("observaciones", "")

        # Validaciones
        if cantidad <= 0:
            return (
                jsonify(
                    {"success": False, "error": "La cantidad debe ser mayor a cero"}
                ),
                400,
            )

        # Reservar usando FIFO
        reservas, faltante = ServicioFIFO.reservar_stock(
            inventario_id=inventario_id,
            cantidad_total=cantidad,
            orden_trabajo_id=orden_trabajo_id,
            documento_referencia=documento_referencia,
            usuario_id=current_user.username,
            observaciones=observaciones,
        )

        db.session.commit()

        # Preparar respuesta
        reservas_data = []
        for lote, cantidad_reservada in reservas:
            reservas_data.append(
                {
                    "lote_id": lote.id,
                    "codigo_lote": lote.codigo_lote or f"Lote-{lote.id}",
                    "cantidad_reservada": cantidad_reservada,
                }
            )

        return jsonify(
            {
                "success": True,
                "reservas": reservas_data,
                "cantidad_faltante": faltante,
                "total_reservado": sum(r[1] for r in reservas),
            }
        )

    except (ValueError, TypeError) as e:
        db.session.rollback()
        return (
            jsonify({"success": False, "error": f"Error en los datos: {str(e)}"}),
            400,
        )
    except Exception as e:
        logger.error(f"Error al reservar stock: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@lotes_bp.route("/api/liberar", methods=["POST"])
@login_required
def api_liberar_reservas():
    """API para liberar reservas de una orden de trabajo"""
    try:
        data = request.get_json()

        # Validar que se recibió JSON
        if not data:
            return jsonify({"success": False, "error": "No se recibieron datos"}), 400

        # Validar campos requeridos
        if "orden_trabajo_id" not in data:
            return (
                jsonify({"success": False, "error": "orden_trabajo_id es requerido"}),
                400,
            )

        orden_trabajo_id = int(data["orden_trabajo_id"])
        observaciones = data.get("observaciones", "")

        # Liberar reservas usando FIFO
        liberaciones = ServicioFIFO.liberar_reservas(
            orden_trabajo_id=orden_trabajo_id,
            usuario_id=current_user.username,
            observaciones=observaciones,
        )

        db.session.commit()

        # Preparar respuesta
        liberaciones_data = []
        for lote, cantidad_liberada in liberaciones:
            liberaciones_data.append(
                {
                    "lote_id": lote.id,
                    "codigo_lote": lote.codigo_lote or f"Lote-{lote.id}",
                    "cantidad_liberada": cantidad_liberada,
                }
            )

        return jsonify(
            {
                "success": True,
                "liberaciones": liberaciones_data,
                "total_liberado": sum(l[1] for l in liberaciones),
            }
        )

    except (ValueError, TypeError) as e:
        db.session.rollback()
        return (
            jsonify({"success": False, "error": f"Error en los datos: {str(e)}"}),
            400,
        )
    except Exception as e:
        logger.error(f"Error al liberar reservas: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@lotes_bp.route("/trazabilidad")
@login_required
def trazabilidad():
    """Página de trazabilidad de lotes"""
    return render_template("lotes/trazabilidad.html")


@lotes_bp.route("/api/trazabilidad/<int:lote_id>")
@login_required
def api_trazabilidad_lote(lote_id):
    """API para obtener trazabilidad completa de un lote"""
    try:
        lote = LoteInventario.query.get_or_404(lote_id)

        # Obtener todos los movimientos del lote
        movimientos = (
            MovimientoLote.query.filter_by(lote_id=lote_id)
            .order_by(MovimientoLote.fecha.asc())
            .all()
        )

        # Preparar datos de trazabilidad
        trazabilidad = {
            "lote": {
                "id": lote.id,
                "codigo_lote": lote.codigo_lote,
                "inventario_codigo": lote.inventario.codigo,
                "inventario_nombre": lote.inventario.nombre,
                "fecha_entrada": lote.fecha_entrada.isoformat(),
                "cantidad_inicial": float(lote.cantidad_inicial),
                "cantidad_actual": float(lote.cantidad_actual),
                "precio_unitario": float(lote.precio_unitario),
                "documento_origen": lote.documento_origen,
                "fecha_vencimiento": (
                    lote.fecha_vencimiento.isoformat()
                    if lote.fecha_vencimiento
                    else None
                ),
                "observaciones": lote.observaciones,
            },
            "movimientos": [],
        }

        for mov in movimientos:
            trazabilidad["movimientos"].append(
                {
                    "fecha": mov.fecha.isoformat(),
                    "tipo": mov.tipo_movimiento,
                    "cantidad": float(mov.cantidad),
                    "documento_referencia": mov.documento_referencia,
                    "observaciones": mov.observaciones,
                    "usuario": mov.usuario_id,
                }
            )

        return jsonify({"success": True, "trazabilidad": trazabilidad})

    except Exception as e:
        logger.error(f"Error al obtener trazabilidad: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@lotes_bp.route("/vencimientos")
@login_required
def vencimientos():
    """Página de productos próximos a vencer"""
    try:
        # Obtener lotes próximos a vencer (próximos 30 días)
        fecha_limite = datetime.now(timezone.utc)

        lotes_proximos = (
            LoteInventario.query.filter(
                LoteInventario.activo == True,
                LoteInventario.cantidad_actual > 0,
                LoteInventario.fecha_vencimiento.isnot(None),
                LoteInventario.fecha_vencimiento > fecha_limite,
            )
            .order_by(LoteInventario.fecha_vencimiento.asc())
            .limit(50)
            .all()
        )

        # Lotes ya vencidos
        lotes_vencidos = (
            LoteInventario.query.filter(
                LoteInventario.activo == True,
                LoteInventario.cantidad_actual > 0,
                LoteInventario.fecha_vencimiento.isnot(None),
                LoteInventario.fecha_vencimiento <= fecha_limite,
            )
            .order_by(LoteInventario.fecha_vencimiento.desc())
            .limit(20)
            .all()
        )

        return render_template(
            "lotes/vencimientos.html",
            lotes_proximos=lotes_proximos,
            lotes_vencidos=lotes_vencidos,
        )

    except Exception as e:
        logger.error(f"Error al obtener vencimientos: {str(e)}")
        flash(f"Error al cargar información de vencimientos: {str(e)}", "error")
        return redirect(url_for("lotes.index"))


@lotes_bp.route("/api/estadisticas")
@login_required
def estadisticas_fifo():
    """Obtener estadísticas rápidas del sistema FIFO"""
    try:
        from sqlalchemy import func, distinct

        # Total de lotes activos
        total_lotes = LoteInventario.query.filter(
            LoteInventario.activo == True, LoteInventario.cantidad_actual > 0
        ).count()

        # Artículos con lotes FIFO
        articulos_con_fifo = (
            db.session.query(func.count(distinct(LoteInventario.inventario_id)))
            .filter(LoteInventario.activo == True, LoteInventario.cantidad_actual > 0)
            .scalar()
            or 0
        )

        # Lotes próximos a vencer (30 días)
        fecha_hoy = datetime.now(timezone.utc)
        fecha_limite = fecha_hoy + timedelta(days=30)

        lotes_proximos_vencer = LoteInventario.query.filter(
            LoteInventario.activo == True,
            LoteInventario.cantidad_actual > 0,
            LoteInventario.fecha_vencimiento.isnot(None),
            LoteInventario.fecha_vencimiento > fecha_hoy,
            LoteInventario.fecha_vencimiento <= fecha_limite,
        ).count()

        # Lotes vencidos
        lotes_vencidos = LoteInventario.query.filter(
            LoteInventario.activo == True,
            LoteInventario.cantidad_actual > 0,
            LoteInventario.fecha_vencimiento.isnot(None),
            LoteInventario.fecha_vencimiento < fecha_hoy,
        ).count()

        # Valor total del inventario
        valor_total = (
            db.session.query(
                func.sum(
                    LoteInventario.cantidad_actual * LoteInventario.precio_unitario
                )
            )
            .filter(LoteInventario.activo == True, LoteInventario.cantidad_actual > 0)
            .scalar()
            or 0
        )

        return jsonify(
            {
                "success": True,
                "estadisticas": {
                    "total_lotes": total_lotes,
                    "articulos_fifo": articulos_con_fifo,
                    "proximos_vencer": lotes_proximos_vencer,
                    "vencidos": lotes_vencidos,
                    "valor_total": float(valor_total),
                },
            }
        )

    except Exception as e:
        logger.error(f"Error al obtener estadísticas FIFO: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "estadisticas": {
                        "total_lotes": 0,
                        "articulos_fifo": 0,
                        "proximos_vencer": 0,
                        "vencidos": 0,
                        "valor_total": 0,
                    },
                }
            ),
            500,
        )


# ==================== TRAZABILIDAD DE LOTES ====================


@lotes_bp.route("/trazabilidad/<int:lote_id>")
@login_required
def ver_trazabilidad(lote_id): # type: ignore
    """Vista de trazabilidad completa de un lote"""
    try:
        lote = LoteInventario.query.get_or_404(lote_id)
        return render_template("lotes/trazabilidad.html", lote=lote)
    except Exception as e:
        logger.error(f"Error al cargar trazabilidad del lote {lote_id}: {str(e)}")
        flash(f"Error al cargar trazabilidad: {str(e)}", "error")
        return redirect(url_for("lotes.index"))


@lotes_bp.route("/api/lotes/<int:lote_id>/trazabilidad")
@login_required
def api_trazabilidad_lote(lote_id):
    """
    API para obtener trazabilidad completa de un lote
    Retorna: información del lote, todos los movimientos, órdenes asociadas, estadísticas
    """
    try:
        # Obtener el lote
        lote = LoteInventario.query.get_or_404(lote_id)

        # Información básica del lote
        lote_info = {
            "id": lote.id,
            "codigo_lote": lote.codigo_lote,
            "inventario": {
                "id": lote.inventario.id,
                "codigo": lote.inventario.codigo,
                "nombre": lote.inventario.nombre,
                "unidad_medida": lote.inventario.unidad_medida,
            },
            "fecha_entrada": (
                lote.fecha_entrada.isoformat() if lote.fecha_entrada else None
            ),
            "fecha_vencimiento": (
                lote.fecha_vencimiento.isoformat() if lote.fecha_vencimiento else None
            ),
            "cantidad_inicial": float(lote.cantidad_inicial),
            "cantidad_actual": float(lote.cantidad_actual),
            "cantidad_reservada": float(lote.cantidad_reservada),
            "precio_unitario": float(lote.precio_unitario),
            "costo_total": float(lote.costo_total),
            "documento_origen": lote.documento_origen,
            "proveedor": (
                {
                    "id": lote.proveedor_id,
                    "nombre": lote.proveedor.nombre if lote.proveedor_id else None,
                }
                if lote.proveedor_id
                else None
            ),
            "activo": lote.activo,
            "esta_vencido": lote.esta_vencido,
            "dias_hasta_vencimiento": lote.dias_hasta_vencimiento,
            "observaciones": lote.observaciones,
            "usuario_creacion": lote.usuario_creacion,
            "fecha_creacion": (
                lote.fecha_creacion.isoformat() if lote.fecha_creacion else None
            ),
        }

        # Obtener todos los movimientos del lote con información extendida
        movimientos = (
            MovimientoLote.query.filter_by(lote_id=lote_id)
            .order_by(MovimientoLote.fecha.desc())
            .all()
        )

        movimientos_data = []
        for mov in movimientos:
            mov_info = {
                "id": mov.id,
                "tipo_movimiento": mov.tipo_movimiento,
                "cantidad": float(mov.cantidad),
                "fecha": mov.fecha.isoformat() if mov.fecha else None,
                "documento_referencia": mov.documento_referencia,
                "observaciones": mov.observaciones,
                "usuario_id": mov.usuario_id,
            }

            # Agregar información de la orden de trabajo si existe
            if mov.orden_trabajo_id:
                from app.models import OrdenTrabajo

                orden = OrdenTrabajo.query.get(mov.orden_trabajo_id)
                if orden:
                    mov_info["orden_trabajo"] = {
                        "id": orden.id,
                        "numero": orden.numero,
                        "descripcion": orden.descripcion,
                        "estado": orden.estado,
                        "activo": orden.activo.codigo if orden.activo else None,
                        "tecnico": orden.tecnico.username if orden.tecnico else None,
                    }

            # Agregar información del movimiento de inventario si existe
            if mov.movimiento_inventario_id:
                from app.models import MovimientoInventario

                mov_inv = MovimientoInventario.query.get(mov.movimiento_inventario_id)
                if mov_inv:
                    mov_info["movimiento_inventario"] = {
                        "id": mov_inv.id,
                        "tipo": mov_inv.tipo,
                        "cantidad": float(mov_inv.cantidad),
                        "motivo": mov_inv.motivo,
                    }

            movimientos_data.append(mov_info)

        # Estadísticas de consumo
        total_consumido = sum(
            float(m.cantidad) for m in movimientos if m.tipo_movimiento == "consumo"
        )
        total_reservado = sum(
            float(m.cantidad) for m in movimientos if m.tipo_movimiento == "reserva"
        )
        total_liberado = sum(
            float(m.cantidad) for m in movimientos if m.tipo_movimiento == "liberacion"
        )
        total_ajustes = sum(
            float(m.cantidad) for m in movimientos if m.tipo_movimiento == "ajuste"
        )

        # Órdenes de trabajo asociadas (únicas)
        ordenes_ids = set(m.orden_trabajo_id for m in movimientos if m.orden_trabajo_id)
        ordenes_info = []
        if ordenes_ids:
            from app.models import OrdenTrabajo

            ordenes = OrdenTrabajo.query.filter(OrdenTrabajo.id.in_(ordenes_ids)).all()
            for orden in ordenes:
                ordenes_info.append(
                    {
                        "id": orden.id,
                        "numero": orden.numero,
                        "descripcion": orden.descripcion,
                        "estado": orden.estado,
                        "fecha_creacion": (
                            orden.fecha_creacion.isoformat()
                            if orden.fecha_creacion
                            else None
                        ),
                        "activo": (
                            {
                                "codigo": orden.activo.codigo,
                                "nombre": orden.activo.nombre,
                            }
                            if orden.activo
                            else None
                        ),
                    }
                )

        # Resumen estadístico
        estadisticas = {
            "total_movimientos": len(movimientos_data),
            "cantidad_consumida": total_consumido,
            "cantidad_reservada": total_reservado,
            "cantidad_liberada": total_liberado,
            "cantidad_ajustada": total_ajustes,
            "porcentaje_utilizado": (
                round((total_consumido / float(lote.cantidad_inicial)) * 100, 2)
                if lote.cantidad_inicial > 0
                else 0
            ),
            "valor_consumido": round(total_consumido * float(lote.precio_unitario), 2),
            "valor_restante": round(
                float(lote.cantidad_actual) * float(lote.precio_unitario), 2
            ),
            "ordenes_asociadas": len(ordenes_info),
            "dias_desde_entrada": (
                (datetime.now(timezone.utc) - lote.fecha_entrada).days
                if lote.fecha_entrada
                else 0
            ),
        }

        return jsonify(
            {
                "success": True,
                "lote": lote_info,
                "movimientos": movimientos_data,
                "ordenes_trabajo": ordenes_info,
                "estadisticas": estadisticas,
            }
        )

    except Exception as e:
        logger.error(f"Error al obtener trazabilidad del lote {lote_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
