from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from datetime import datetime, timedelta
from app.models.orden_trabajo import OrdenTrabajo
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.activo import Activo
from sqlalchemy import func, and_, or_
import calendar

calendario_bp = Blueprint("calendario", __name__, url_prefix="/calendario")


@calendario_bp.route("/")
@login_required
def calendario_page():
    """Página principal del calendario de órdenes"""
    return render_template("calendario/calendario.html", section="calendario")


@calendario_bp.route("/api/ordenes")
@login_required
def obtener_ordenes_calendario():
    """Obtener órdenes para mostrar en el calendario"""
    try:
        # Obtener parámetros de fecha (mes/año)
        year = request.args.get("year", datetime.now().year, type=int)
        month = request.args.get("month", datetime.now().month, type=int)

        # Calcular rango de fechas para el mes (incluyendo todo el día)
        primer_dia = datetime(year, month, 1, 0, 0, 0)
        if month == 12:
            ultimo_dia = datetime(year + 1, 1, 1, 23, 59, 59)
        else:
            ultimo_dia = datetime(year, month + 1, 1, 23, 59, 59)

        print(
            f"🔍 DEBUG Calendario - Buscando órdenes entre {primer_dia} y {ultimo_dia}"
        )

        # Obtener órdenes del mes
        # Buscar tanto por fecha_programada como por fecha_creacion
        ordenes = OrdenTrabajo.query.filter(
            or_(
                and_(
                    OrdenTrabajo.fecha_programada >= primer_dia,
                    OrdenTrabajo.fecha_programada <= ultimo_dia,
                ),
                and_(
                    OrdenTrabajo.fecha_creacion >= primer_dia,
                    OrdenTrabajo.fecha_creacion <= ultimo_dia,
                ),
            )
        ).all()

        print(f"📊 DEBUG Calendario - Encontradas {len(ordenes)} órdenes")
        for orden in ordenes[:10]:  # Mostrar primeras 10 para debug
            print(
                f"   - {orden.numero_orden}: ID={orden.id}, Programada={orden.fecha_programada}, Creada={orden.fecha_creacion}, Estado={orden.estado}"
            )

        # Obtener planes próximos (para mostrar futuras generaciones)
        planes_proximos = PlanMantenimiento.query.filter(
            and_(
                PlanMantenimiento.estado == "Activo",
                PlanMantenimiento.proxima_ejecucion >= primer_dia,
                PlanMantenimiento.proxima_ejecucion <= ultimo_dia,
            )
        ).all()

        eventos = []

        # Agregar órdenes existentes
        for orden in ordenes:
            color = {
                "Pendiente": "#ffc107",  # Amarillo
                "En Proceso": "#17a2b8",  # Azul
                "Completada": "#28a745",  # Verde
                "Cancelada": "#dc3545",  # Rojo
            }.get(
                orden.estado, "#6c757d"
            )  # Gris por defecto

            # Usar fecha_programada si existe, si no usar fecha_creacion
            fecha_evento = (
                orden.fecha_programada
                if orden.fecha_programada
                else orden.fecha_creacion
            )

            # Convertir a formato ISO para FullCalendar
            fecha_iso = None
            if fecha_evento:
                try:
                    if isinstance(fecha_evento, datetime):
                        fecha_iso = fecha_evento.date().isoformat()
                    elif isinstance(fecha_evento, str):
                        # Si ya es string, intentar parsearlo
                        dt = datetime.fromisoformat(fecha_evento.replace("Z", "+00:00"))
                        fecha_iso = dt.date().isoformat()
                    else:
                        # Asumir que es objeto date
                        fecha_iso = fecha_evento.isoformat()

                    print(
                        f"   📅 {orden.numero_orden}: fecha_evento={fecha_evento} -> fecha_iso={fecha_iso}"
                    )
                except Exception as e:
                    print(
                        f"   ⚠️ Error convirtiendo fecha para {orden.numero_orden}: {e}"
                    )
                    fecha_iso = None

            if not fecha_iso:
                print(f"   ❌ {orden.numero_orden}: Sin fecha válida, saltando...")
                continue

            eventos.append(
                {
                    "id": f"orden-{orden.id}",
                    "title": f"{orden.numero_orden}",
                    "description": orden.descripcion[:50]
                    + ("..." if len(orden.descripcion) > 50 else ""),
                    "start": fecha_iso,
                    "backgroundColor": color,
                    "borderColor": color,
                    "tipo": "orden",
                    "estado": orden.estado,
                    "prioridad": orden.prioridad,
                    "activo_id": orden.activo_id,
                }
            )

        # Agregar planes futuros (órdenes que se generarán)
        for plan in planes_proximos:
            activo = Activo.query.get(plan.activo_id) if plan.activo_id else None

            eventos.append(
                {
                    "id": f"plan-{plan.id}",
                    "title": f"📅 {plan.codigo_plan}",
                    "description": f"Mantenimiento preventivo: {plan.nombre}",
                    "start": plan.proxima_ejecucion.isoformat(),
                    "backgroundColor": "#6f42c1",  # Púrpura para planes
                    "borderColor": "#6f42c1",
                    "tipo": "plan_futuro",
                    "activo_nombre": activo.nombre if activo else "Sin activo",
                    "frecuencia": plan.frecuencia,
                }
            )

        print(
            f"✅ DEBUG Calendario - Total eventos creados: {len(eventos)} (órdenes: {len([e for e in eventos if e['tipo'] == 'orden'])}, planes: {len([e for e in eventos if e['tipo'] == 'plan_futuro'])})"
        )

        return jsonify(
            {
                "success": True,
                "eventos": eventos,
                "mes": month,
                "anio": year,
                "total_ordenes": len(ordenes),
                "total_planes": len(planes_proximos),
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@calendario_bp.route("/api/estadisticas-mes")
@login_required
def estadisticas_mes():
    """Obtener estadísticas del mes para el calendario"""
    try:
        year = request.args.get("year", datetime.now().year, type=int)
        month = request.args.get("month", datetime.now().month, type=int)

        primer_dia = datetime(year, month, 1)
        if month == 12:
            ultimo_dia = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia = datetime(year, month + 1, 1) - timedelta(days=1)

        # Estadísticas de órdenes
        ordenes_stats = (
            OrdenTrabajo.query.filter(
                and_(
                    OrdenTrabajo.fecha_programada >= primer_dia,
                    OrdenTrabajo.fecha_programada <= ultimo_dia,
                )
            )
            .with_entities(
                OrdenTrabajo.estado, func.count(OrdenTrabajo.id).label("cantidad")
            )
            .group_by(OrdenTrabajo.estado)
            .all()
        )

        # Planes que ejecutarán este mes
        planes_mes = PlanMantenimiento.query.filter(
            and_(
                PlanMantenimiento.estado == "Activo",
                PlanMantenimiento.proxima_ejecucion >= primer_dia,
                PlanMantenimiento.proxima_ejecucion <= ultimo_dia,
            )
        ).count()

        # Formatear estadísticas
        stats_formateadas = {}
        total_ordenes = 0

        for estado, cantidad in ordenes_stats:
            stats_formateadas[estado] = cantidad
            total_ordenes += cantidad

        return jsonify(
            {
                "success": True,
                "ordenes_por_estado": stats_formateadas,
                "total_ordenes": total_ordenes,
                "planes_programados": planes_mes,
                "mes_nombre": calendar.month_name[month],
                "anio": year,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@calendario_bp.route("/api/generar-ordenes-fecha")
@login_required
def generar_ordenes_fecha_especifica():
    """Generar órdenes para una fecha específica"""
    try:
        fecha_str = request.args.get("fecha")
        if not fecha_str:
            return jsonify({"success": False, "error": "Fecha requerida"}), 400

        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")

        # Buscar planes que deberían ejecutarse en esa fecha o antes
        planes_vencidos = PlanMantenimiento.query.filter(
            and_(
                PlanMantenimiento.estado == "Activo",
                PlanMantenimiento.proxima_ejecucion <= fecha,
            )
        ).all()

        from app.controllers.planes_controller import generar_ordenes_automaticas

        resultado = generar_ordenes_automaticas()

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
