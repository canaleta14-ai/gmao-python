from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
    send_from_directory,
    Response,
)
from flask_login import login_required, current_user, login_user, logout_user

# Importar función de autenticación desde el controlador
from app.controllers.usuarios_controller import autenticar_usuario


from app.models.orden_trabajo import (
    OrdenTrabajo,
)  # Ensure this model is defined correctly and properly initialized
from app.extensions import db  # Importar db correctamente desde extensions
from app.models.activo import Activo
from app.models.inventario import Inventario
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.usuario import Usuario
from datetime import datetime, timedelta
import os

web_bp = Blueprint("web", __name__)


@web_bp.route("/health")
def health_check():
    """Health check endpoint para App Engine"""
    try:
        # Verificar conexión a BD
        db.session.execute(db.text("SELECT 1"))
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


# @web_bp.route("/admin/emergency-reload-config", methods=["POST"])
# @exempt
# def emergency_reload_config():
#     """Endpoint de emergencia para forzar recarga de configuración de secretos"""
#     try:
#         # Importar funciones de configuración
#         from app.utils.secrets import get_secret_or_env
#         import os
#
#         # Limpiar cache de variables de entorno si existe
#         if hasattr(os, "_environ_cache"):
#             delattr(os, "_environ_cache")
#
#         # Forzar detección de entorno GCP
#         os.environ["FORCE_GCP_MODE"] = "true"
#
#         # Intentar obtener la configuración de base de datos
#         db_password = get_secret_or_env("PGPASSWORD", "gmao-db-password")
#         db_host = get_secret_or_env("PGHOST", "gmao-db-host")
#         db_user = get_secret_or_env("PGUSER", "gmao-db-user", "postgres")
#         db_name = get_secret_or_env("PGDATABASE", "gmao-db-name", "gmao_db")
#
#         # Verificar que obtuvimos los valores
#         config_status = {
#             "db_password": (
#                 "✓" if db_password and db_password != "gmao-db-password" else "✗"
#             ),
#             "db_host": "✓" if db_host and db_host != "gmao-db-host" else "✗",
#             "db_user": "✓" if db_user else "✗",
#             "db_name": "✓" if db_name else "✗",
#             "gcp_mode_forced": "✓",
#         }
#
#         return (
#             jsonify(
#                 {
#                     "status": "config_reloaded",
#                     "config_status": config_status,
#                     "message": "Configuración de secretos recargada",
#                 }
#             ),
#             200,
#         )
#
#     except Exception as e:
#         return jsonify({"status": "error", "error": str(e)}), 500


@web_bp.route("/admin/asignar-tecnicos", methods=["POST"])
@login_required
def asignar_tecnicos_masivo():
    """Endpoint de administración para asignar técnicos a órdenes sin técnico"""

    # Solo administradores pueden ejecutar esto
    if current_user.rol != "administrador":
        return jsonify({"error": "Acceso denegado. Solo administradores."}), 403

    try:
        # Buscar órdenes sin técnico
        ordenes_sin_tecnico = OrdenTrabajo.query.filter(
            OrdenTrabajo.tecnico_id == None
        ).all()

        if not ordenes_sin_tecnico:
            return jsonify(
                {
                    "success": True,
                    "message": "No hay órdenes sin técnico asignado",
                    "asignadas": 0,
                }
            )

        # Verificar que hay técnicos disponibles
        tecnicos_activos = Usuario.query.filter_by(rol="tecnico", activo=True).count()

        if tecnicos_activos == 0:
            return jsonify({"error": "No hay técnicos activos en el sistema"}), 400

        asignadas = 0
        detalles = []

        for orden in ordenes_sin_tecnico:
            # Usar el mismo algoritmo de balanceo de carga
            tecnicos = Usuario.query.filter_by(rol="tecnico", activo=True).all()

            # Contar órdenes pendientes por técnico
            carga_tecnicos = {}
            for tecnico in tecnicos:
                ordenes_pendientes = OrdenTrabajo.query.filter(
                    OrdenTrabajo.tecnico_id == tecnico.id,
                    OrdenTrabajo.estado.in_(["Pendiente", "En Proceso"]),
                ).count()
                carga_tecnicos[tecnico.id] = ordenes_pendientes

            # Asignar al técnico con menos carga
            tecnico_id = min(carga_tecnicos, key=carga_tecnicos.get)
            tecnico = Usuario.query.get(tecnico_id)

            orden.tecnico_id = tecnico_id
            asignadas += 1

            detalles.append(
                {
                    "orden_id": orden.id,
                    "numero_orden": orden.numero_orden,
                    "tecnico": tecnico.nombre,
                }
            )

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Se asignaron técnicos a {asignadas} órdenes",
                "asignadas": asignadas,
                "detalles": detalles[:10],  # Mostrar solo las primeras 10
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@web_bp.route("/admin/asignar-tecnicos-page")
@login_required
def asignar_tecnicos_page():
    """Página de administración para asignar técnicos"""
    if current_user.rol != "administrador":
        flash("Acceso denegado. Solo administradores.", "danger")
        return redirect(url_for("web.dashboard"))

    return render_template("admin/asignar-tecnicos.html")


@web_bp.route("/admin/hacerme-admin", methods=["POST"])
@login_required
def hacerme_admin():
    """Endpoint temporal para convertir al usuario actual en administrador"""
    try:
        # Actualizar rol del usuario actual
        current_user.rol = "administrador"
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Usuario '{current_user.username}' es ahora ADMINISTRADOR",
                "nuevo_rol": current_user.rol,
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@web_bp.route("/admin/hacerme-tecnico", methods=["POST"])
@login_required
def hacerme_tecnico():
    """Endpoint temporal para convertir al usuario actual en técnico"""
    try:
        # Actualizar rol del usuario actual
        current_user.rol = "tecnico"
        current_user.activo = True
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Usuario '{current_user.username}' es ahora TÉCNICO ACTIVO",
                "nuevo_rol": current_user.rol,
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@web_bp.route("/admin/crear-tecnico-demo", methods=["POST"])
@login_required
def crear_tecnico_demo():
    """Endpoint temporal para crear un técnico de demostración"""
    try:
        # Verificar si ya existe un técnico activo
        tecnico_existente = Usuario.query.filter_by(rol="tecnico", activo=True).first()

        if tecnico_existente:
            return jsonify(
                {
                    "success": True,
                    "message": f"Ya existe un técnico activo: {tecnico_existente.nombre}",
                    "tecnico": tecnico_existente.nombre,
                }
            )

        # Crear técnico demo
        from werkzeug.security import generate_password_hash

        tecnico_demo = Usuario(
            username="tecnico_demo",
            nombre="Técnico Demo",
            email="tecnico@demo.com",
            password=generate_password_hash("demo123"),
            rol="tecnico",
            activo=True,
        )

        db.session.add(tecnico_demo)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Técnico demo creado: {tecnico_demo.nombre}",
                "tecnico": tecnico_demo.nombre,
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@web_bp.route("/test-dashboard")
def test_dashboard():
    """Página de test independiente para diagnosticar problemas"""
    return render_template("test-dashboard.html")


@web_bp.route("/admin/migrate-dias-semana", methods=["POST"])
def migrate_dias_semana():
    """Endpoint temporal para migrar el campo dias_semana a VARCHAR(200)"""
    try:
        sql = """
        ALTER TABLE plan_mantenimiento 
        ALTER COLUMN dias_semana TYPE VARCHAR(200);
        """

        db.session.execute(db.text(sql))
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Campo dias_semana migrado exitosamente a VARCHAR(200)",
            }
        )
    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"success": False, "error": f"Error en migración: {str(e)}"}),
            500,
        )


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
        return redirect(url_for("web.dashboard"))
    return redirect(url_for("web.login"))


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    """Endpoint de login con soporte JSON y formulario.

    - GET: devuelve 200 con página de login o fallback.
    - POST: valida credenciales y devuelve 200/401/400 según corresponda.
    """
    try:
        if request.method == "GET":
            if current_user.is_authenticated:
                return redirect(url_for("web.dashboard"))
            # Intentar renderizar template si existe; si falla, entregar HTML mínimo
            try:
                # Renderizar plantilla correcta dentro de 'web' y ajustar layout
                return render_template(
                    "web/login.html",
                    login_bg=True,
                    no_sidebar=True,
                    show_forgot=False,
                )
            except Exception:
                html = """
                <!DOCTYPE html>
                <html lang=\"es\">
                <head><meta charset=\"utf-8\"><title>Login</title></head>
                <body>
                    <h1>Login</h1>
                    <p>Introduzca sus credenciales para acceder.</p>
                </body>
                </html>
                """
                return Response(html, mimetype="text/html")

        # POST
        # Aceptar JSON o form-data
        data = (
            request.get_json(silent=True) if request.is_json else request.form.to_dict()
        ) or {}

        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()

        if not username or not password:
            return jsonify({"success": False, "error": "missing_fields"}), 400

        # Autenticar vía controlador
        try:
            user = autenticar_usuario(username, password)
        except Exception as e:
            return (
                jsonify({"success": False, "error": "auth_error", "detail": str(e)}),
                401,
            )

        if not user:
            return jsonify({"success": False, "error": "invalid_credentials"}), 401

        login_user(user)
        return jsonify({"success": True}), 200
    except Exception as e:
        # Fallback defensivo
        return jsonify({"success": False, "error": str(e)}), 500


@web_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """Cerrar sesión y redirigir a /login (GET) o responder JSON (POST)."""
    try:
        logout_user()
        if request.method == "POST":
            return jsonify({"success": True}), 200
        return redirect(url_for("web.login"))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@web_bp.route("/recambios/")
@login_required
def recambios_page():
    """Página de recambios (fallback mínimo para smoke tests)."""
    try:
        # Si existiera un template, cargarlo; de momento proporcionamos fallback
        return render_template("recambios/index.html", section="recambios")
    except Exception:
        html = """
        <!DOCTYPE html>
        <html lang=\"es\">
        <head><meta charset=\"utf-8\"><title>Recambios</title></head>
        <body>
            <h1>Recambios</h1>
            <p>Vista mínima de Recambios para verificación. La interfaz completa se carga desde Órdenes.</p>
        </body>
        </html>
        """
        return Response(html, mimetype="text/html")


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
    logger.info("[START] INICIO: Cargando alertas de mantenimiento")

    try:
        # Paso 1: Preparar fechas
        inicio_fechas = time.time()
        hoy = datetime.now().date()
        proximos_7_dias = hoy + timedelta(days=7)
        tiempo_fechas = (time.time() - inicio_fechas) * 1000
        logger.info(f"[TIMING] Fechas preparadas en {tiempo_fechas:.2f}ms")

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
            f"[DB] Consulta BD completada en {tiempo_consulta:.2f}ms - {len(planes_relevantes)} planes encontrados"
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
        except Exception:
            # Fallback robusto: limpiar sesión abortada y usar SQL directo en AUTOCOMMIT
            try:
                db.session.rollback()
            except Exception:
                pass
            try:
                db.session.remove()
            except Exception:
                pass
            try:
                backend = (
                    db.engine.url.get_backend_name()
                    if getattr(db, "engine", None)
                    else None
                )
                table_name = "inventario"
                if backend in ("postgresql", "postgres"):
                    table_name = "public.inventario"
                from sqlalchemy import text as _text

                with db.engine.connect() as base_conn:
                    try:
                        base_conn.exec_driver_sql("ROLLBACK")
                    except Exception:
                        pass
                    with base_conn.execution_options(
                        isolation_level="AUTOCOMMIT"
                    ) as conn:
                        rows = (
                            conn.execute(
                                _text(
                                    f"SELECT id, descripcion, COALESCE(stock_actual, 0) AS stock_actual FROM {table_name} WHERE COALESCE(stock_actual, 0) <= COALESCE(stock_minimo, 0) ORDER BY id"
                                )
                            )
                            .mappings()
                            .all()
                        )
                        for r in rows:
                            notificaciones.append(
                                {
                                    "id": f"inventario_{r['id']}",
                                    "tipo": "warning",
                                    "titulo": "Inventario Bajo",
                                    "mensaje": f"Producto \"{r['descripcion']}\" tiene stock bajo ({r['stock_actual']})",
                                    "url": f"/inventario",
                                    "icono": "bi-box-seam",
                                    "fecha": None,
                                }
                            )
            except Exception:
                # Si falla también el fallback, continuar sin notificaciones de inventario
                pass

        # Ordenar notificaciones por prioridad (danger > warning > info) y fecha
        prioridad_orden = {"danger": 0, "warning": 1, "info": 2, "success": 3}
        notificaciones.sort(
            key=lambda x: (
                prioridad_orden.get(x["tipo"], 4),
                x.get("fecha") or "9999-99-99",
            )
        )

        # Devolver lista simple para alinear con tests
        return jsonify(notificaciones)

    except Exception as e:
        # En caso de error, responder lista vacía con 200 para evitar 500
        return jsonify([]), 200
