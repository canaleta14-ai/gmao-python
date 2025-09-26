from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
    send_from_directory,
)
from flask_login import login_required, current_user, logout_user
from app.controllers.usuarios_controller import autenticar_usuario
from app.models.orden_trabajo import (
    OrdenTrabajo,
)  # Ensure this model is defined correctly and properly initialized
from app.extensions import db  # Importar db correctamente desde extensions
from app.models.activo import Activo
from app.models.inventario import Inventario
from app.models.plan_mantenimiento import PlanMantenimiento
from datetime import datetime, timedelta
import os

web_bp = Blueprint("web", __name__)


@web_bp.route("/test-dashboard")
def test_dashboard():
    """Página de test independiente para diagnosticar problemas"""
    return render_template("test-dashboard.html")


@web_bp.route("/alertas-test")
def alertas_test():
    """Página de prueba específica para alertas de mantenimiento"""
    return render_template("alertas-test.html")


@web_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("web.dashboard"))
    return redirect(url_for("web.login"))


@web_bp.route("/dashboard")
@login_required
def dashboard():
    from datetime import date
    from sqlalchemy import func
    from app.models.orden_trabajo import OrdenTrabajo

    hoy = date.today()
    stats: dict[str, int] = {
        "ordenes_activas": OrdenTrabajo.query.filter_by(estado="En Proceso").count(),
        "ordenes_completadas_hoy": OrdenTrabajo.query.filter(
            OrdenTrabajo.estado == "Completada",
            func.date(OrdenTrabajo.fecha_completada) == hoy,
        ).count(),
        "ordenes_pendientes": OrdenTrabajo.query.filter_by(estado="Pendiente").count(),
        "total_activos": Activo.query.count(),
        "activos_operativos": Activo.query.filter_by(estado="Operativo").count(),
        "activos_mantenimiento": Activo.query.filter_by(
            estado="En Mantenimiento"
        ).count(),
        "inventario_bajo": Inventario.query.filter(
            Inventario.stock_actual <= Inventario.stock_minimo
        ).count(),
    }

    ordenes_recientes = (
        OrdenTrabajo.query.order_by(OrdenTrabajo.fecha_creacion.desc()).limit(10).all()
    )
    return render_template(
        "dashboard/dashboard.html", stats=stats, ordenes_recientes=ordenes_recientes
    )


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form
        username = data.get("username")
        password = data.get("password")
        user = autenticar_usuario(username, password)
        if user:
            if request.is_json:
                return jsonify({"success": True, "message": "Login exitoso"})
            flash("Login exitoso", "success")
            return redirect(url_for("web.dashboard"))
        else:
            if request.is_json:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Usuario o contraseña incorrectos",
                        }
                    ),
                    401,
                )
            flash("Usuario o contraseña incorrectos", "danger")
            return render_template("web/login.html", no_sidebar=True, login_bg=True)
    return render_template("web/login.html", no_sidebar=True, login_bg=True)


@web_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("web.login"))


@web_bp.route("/api/user/info")
@login_required
def get_user_info():
    """Obtener información del usuario actual"""
    if current_user.is_authenticated:
        return jsonify(
            {
                "success": True,
                "user": {
                    "id": current_user.id,
                    "username": current_user.username,
                    "email": current_user.email,
                    "nombre": getattr(current_user, "nombre", None)
                    or current_user.username,
                    "rol": current_user.rol,
                    "activo": current_user.activo,
                },
            }
        )
    else:
        return jsonify({"success": False, "error": "Usuario no autenticado"}), 401


@web_bp.route("/reportes")
@login_required
def reportes():
    """Página de reportes de mantenimiento"""
    return render_template("reportes/reportes.html")


@web_bp.route("/api/alertas-mantenimiento")
@login_required
def alertas_mantenimiento():
    """API para obtener alertas de mantenimiento preventivo - Optimizado con debugging"""
    import time
    import logging

    # Configurar logging para esta función
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    inicio_total = time.time()
    logger.info("🚀 INICIO: Cargando alertas de mantenimiento")

    try:
        # Paso 1: Preparar fechas
        inicio_fechas = time.time()
        hoy = datetime.now().date()
        proximos_7_dias = hoy + timedelta(days=7)
        tiempo_fechas = (time.time() - inicio_fechas) * 1000
        logger.info(f"‚è∞ Fechas preparadas en {tiempo_fechas:.2f}ms")

        # Paso 2: Consulta a base de datos
        inicio_consulta = time.time()
        planes_relevantes = (
            PlanMantenimiento.query.filter(
                PlanMantenimiento.estado == "Activo",
                PlanMantenimiento.proxima_ejecucion.isnot(None),
                db.func.date(PlanMantenimiento.proxima_ejecucion) <= proximos_7_dias,
            )
            .join(Activo)  # Join para acceso eficiente al activo
            .order_by(PlanMantenimiento.proxima_ejecucion.asc())  # Pre-ordenar en BD
            .all()
        )
        tiempo_consulta = (time.time() - inicio_consulta) * 1000
        logger.info(
            f"üóÑ Consulta BD completada en {tiempo_consulta:.2f}ms - {len(planes_relevantes)} planes encontrados"
        )

        alertas = []
        vencidos_count = 0
        proximos_count = 0

        # Procesar todos los planes en un solo bucle
        for plan in planes_relevantes:
            fecha_vencimiento = plan.proxima_ejecucion.date()

            if fecha_vencimiento < hoy:
                # Plan vencido
                dias_vencido = (hoy - fecha_vencimiento).days
                vencidos_count += 1
                alertas.append(
                    {
                        "id": plan.id,
                        "tipo": "vencido",
                        "titulo": f"Mantenimiento Vencido: {plan.nombre}",
                        "descripcion": f"El plan de mantenimiento para {plan.activo.nombre} está vencido por {dias_vencido} días",
                        "activo": plan.activo.nombre,
                        "fecha_vencimiento": fecha_vencimiento.strftime("%Y-%m-%d"),
                        "dias_vencido": dias_vencido,
                        "prioridad": "alta" if dias_vencido > 3 else "media",
                    }
                )
            else:
                # Plan próximo a vencer
                dias_restantes = (fecha_vencimiento - hoy).days
                proximos_count += 1
                alertas.append(
                    {
                        "id": plan.id,
                        "tipo": "proximo",
                        "titulo": f"Mantenimiento Próximo: {plan.nombre}",
                        "descripcion": f"El plan de mantenimiento para {plan.activo.nombre} vence en {dias_restantes} días",
                        "activo": plan.activo.nombre,
                        "fecha_vencimiento": fecha_vencimiento.strftime("%Y-%m-%d"),
                        "dias_restantes": dias_restantes,
                        "prioridad": (
                            "alta"
                            if dias_restantes <= 1
                            else "media" if dias_restantes <= 3 else "baja"
                        ),
                    }
                )

        # Ordenar alertas por prioridad (vencidos primero, luego por días)
        def prioridad_orden(alerta):
            prioridades = {"alta": 1, "media": 2, "baja": 3}
            if alerta["tipo"] == "vencido":
                return (
                    0,
                    prioridades.get(alerta["prioridad"], 4),
                    -alerta["dias_vencido"],
                )
            else:
                return (
                    1,
                    prioridades.get(alerta["prioridad"], 4),
                    alerta["dias_restantes"],
                )

        alertas.sort(key=prioridad_orden)

        return jsonify(
            {
                "success": True,
                "alertas": alertas,
                "total": len(alertas),
                "vencidos": vencidos_count,
                "proximos": proximos_count,
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "alertas": [],
                    "total": 0,
                    "vencidos": 0,
                    "proximos": 0,
                }
            ),
            500,
        )


@web_bp.route("/test-codigo-automatico")
def test_codigo_automatico():
    """Página de prueba para generación automática de códigos"""
    return render_template("test_codigo_automatico.html")
