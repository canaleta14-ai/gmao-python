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
from datetime import datetime, timezone
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


@lotes_bp.route("/api/consumir", methods=["POST"])
@login_required
def api_consumir_fifo():
    """API para consumir stock usando FIFO"""
    try:
        data = request.get_json()

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

    except ValueError as e:
        return (
            jsonify({"success": False, "error": f"Error en los datos: {str(e)}"}),
            400,
        )
    except Exception as e:
        logger.error(f"Error al consumir FIFO: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@lotes_bp.route("/api/reservar", methods=["POST"])
@login_required
def api_reservar_stock():
    """API para reservar stock usando FIFO"""
    try:
        data = request.get_json()

        inventario_id = int(data["inventario_id"])
        cantidad = float(data["cantidad"])
        orden_trabajo_id = int(data["orden_trabajo_id"])
        documento_referencia = data.get("documento_referencia", "")
        observaciones = data.get("observaciones", "")

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

    except ValueError as e:
        return (
            jsonify({"success": False, "error": f"Error en los datos: {str(e)}"}),
            400,
        )
    except Exception as e:
        logger.error(f"Error al reservar stock: {str(e)}")
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
