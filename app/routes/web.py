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
from flask_login import login_required, current_user

# Importar función de autenticación desde el controlador
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

web_bp = Blueprint("web_routes", __name__)


@web_bp.route("/health")
def health_check():
    """Health check endpoint para App Engine"""
    try:
        # Verificar conexión a BD
        db.session.execute(db.text("SELECT 1"))
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


@web_bp.route("/test-dashboard")
def test_dashboard():
    """Página de test independiente para diagnosticar problemas"""
    return render_template("test-dashboard.html")


@web_bp.route("/test-notificaciones")
def test_notificaciones():
    """Página de prueba para las nuevas notificaciones de Bootstrap"""
    return render_template("test-notificaciones.html")


@web_bp.route("/alertas-test")
def alertas_test():
    """Página de prueba específica para alertas de mantenimiento"""
    return render_template("alertas-test.html")


@web_bp.route("/test-modales")
def test_modales():
    """Página de prueba para modales de confirmación modernos"""
    return render_template("test-modales.html")


@web_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("web_routes.dashboard"))
    return redirect(url_for("usuarios_controller.login"))


@web_bp.route("/dashboard")
@login_required
def dashboard():
    # El dashboard ahora obtiene los datos via JavaScript/API
    # No necesitamos hacer consultas aquí
    return render_template("dashboard/dashboard.html")


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


@web_bp.route("/api/notificaciones")
@login_required
def get_notificaciones():
    """Obtener notificaciones del sistema para el usuario actual"""
    try:
        notificaciones = []

        # 1. Planes de mantenimiento próximos a vencer (dentro de 7 días)
        hoy = datetime.now().date()
        fecha_limite = hoy + timedelta(days=7)

        planes_proximos = PlanMantenimiento.query.filter(
            PlanMantenimiento.proxima_ejecucion <= fecha_limite,
            PlanMantenimiento.proxima_ejecucion >= hoy,
            PlanMantenimiento.estado == "Activo",
        ).all()

        for plan in planes_proximos:
            dias_restantes = (plan.proxima_ejecucion - hoy).days
            notificaciones.append(
                {
                    "id": f"plan_{plan.id}",
                    "tipo": "warning",
                    "titulo": "Mantenimiento Próximo",
                    "mensaje": f'Plan "{plan.nombre}" vence en {dias_restantes} día(s)',
                    "url": f"/planes",
                    "icono": "bi-calendar-event",
                    "fecha": plan.proxima_ejecucion.isoformat(),
                }
            )

        # 2. Planes de mantenimiento vencidos
        planes_vencidos = PlanMantenimiento.query.filter(
            PlanMantenimiento.proxima_ejecucion < hoy,
            PlanMantenimiento.estado == "Activo",
        ).all()

        for plan in planes_vencidos:
            dias_vencido = (hoy - plan.proxima_ejecucion).days
            notificaciones.append(
                {
                    "id": f"plan_vencido_{plan.id}",
                    "tipo": "danger",
                    "titulo": "Mantenimiento Vencido",
                    "mensaje": f'Plan "{plan.nombre}" venció hace {dias_vencido} día(s)',
                    "url": f"/planes",
                    "icono": "bi-exclamation-triangle",
                    "fecha": plan.proxima_ejecucion.isoformat(),
                }
            )

        # 3. Órdenes de trabajo pendientes
        ordenes_pendientes = OrdenTrabajo.query.filter(
            OrdenTrabajo.estado.in_(["Pendiente", "En Progreso"])
        ).all()

        for orden in ordenes_pendientes:
            notificaciones.append(
                {
                    "id": f"orden_{orden.id}",
                    "tipo": "info",
                    "titulo": "Orden Pendiente",
                    "mensaje": f'Orden "{orden.titulo}" requiere atención',
                    "url": f"/ordenes",
                    "icono": "bi-clipboard-check",
                    "fecha": (
                        orden.fecha_creacion.isoformat()
                        if orden.fecha_creacion
                        else None
                    ),
                }
            )

        # 4. Inventario bajo (si hay productos con stock bajo)
        try:
            inventario_bajo = Inventario.query.filter(
                Inventario.stock_actual <= Inventario.stock_minimo
            ).all()

            for item in inventario_bajo:
                notificaciones.append(
                    {
                        "id": f"inventario_{item.id}",
                        "tipo": "warning",
                        "titulo": "Inventario Bajo",
                        "mensaje": f'Producto "{item.descripcion}" tiene stock bajo ({item.stock_actual})',
                        "url": f"/inventario",
                        "icono": "bi-box-seam",
                        "fecha": None,
                    }
                )
        except:
            # Si hay error con inventario, continuar sin esta notificación
            pass

        # Ordenar notificaciones por prioridad (danger > warning > info) y fecha
        prioridad_orden = {"danger": 0, "warning": 1, "info": 2, "success": 3}
        notificaciones.sort(
            key=lambda x: (
                prioridad_orden.get(x["tipo"], 4),
                x.get("fecha") or "9999-99-99",
            )
        )

        return jsonify(
            {
                "success": True,
                "notificaciones": notificaciones,
                "total": len(notificaciones),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {"success": False, "error": str(e), "notificaciones": [], "total": 0}
            ),
            500,
        )
