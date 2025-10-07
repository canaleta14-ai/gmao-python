"""
Endpoints para tareas programadas (cron jobs)
Protegidos con X-Appengine-Cron header
"""

from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.orden_trabajo import OrdenTrabajo
from app.models.activo import Activo
from app.models.usuario import Usuario
from datetime import datetime, timezone, timedelta
from sqlalchemy import and_
import logging

logger = logging.getLogger(__name__)

cron_bp = Blueprint("cron", __name__, url_prefix="/api/cron")


def is_valid_cron_request():
    """
    Verificar que la petición viene de Cloud Scheduler
    En App Engine, el header X-Appengine-Cron solo puede ser
    establecido por el sistema, no por usuarios externos
    """
    # En desarrollo, permitir sin header
    if current_app.config.get("FLASK_ENV") == "development":
        return True

    # En producción, verificar header de App Engine
    return request.headers.get("X-Appengine-Cron") == "true"


@cron_bp.route("/generar-ordenes-preventivas", methods=["GET", "POST"])
def generar_ordenes_preventivas():
    """
    Genera órdenes de trabajo para planes de mantenimiento vencidos

    Ejecutado por Cloud Scheduler diariamente a las 00:00 AM

    Returns:
        JSON con resumen de órdenes generadas
    """
    # Verificar que la petición es válida
    if not is_valid_cron_request():
        logger.warning("Intento de acceso no autorizado a endpoint de cron")
        return (
            jsonify(
                {
                    "error": "Acceso no autorizado",
                    "mensaje": "Este endpoint solo puede ser llamado por Cloud Scheduler",
                }
            ),
            403,
        )

    try:
        logger.info("=== INICIO: Generación automática de órdenes preventivas ===")

        # Obtener fecha/hora actual en UTC
        ahora_utc = datetime.now(timezone.utc)

        # Buscar planes activos con generación automática que necesitan ejecución
        # (próxima_ejecucion <= ahora)
        planes_vencidos = PlanMantenimiento.query.filter(
            and_(
                PlanMantenimiento.estado == "Activo",
                PlanMantenimiento.generacion_automatica == True,
                PlanMantenimiento.proxima_ejecucion <= ahora_utc,
            )
        ).all()

        logger.info(f"Planes vencidos encontrados: {len(planes_vencidos)}")

        ordenes_creadas = []
        errores = []

        for plan in planes_vencidos:
            try:
                # Generar orden de trabajo
                orden = crear_orden_desde_plan(plan)

                if orden:
                    ordenes_creadas.append(
                        {
                            "orden_id": orden.id,
                            "numero_orden": orden.numero_orden,
                            "plan_id": plan.id,
                            "activo": plan.activo.nombre if plan.activo else "N/A",
                            "descripcion": orden.descripcion,
                        }
                    )

                    logger.info(
                        f"✅ Orden creada: {orden.numero_orden} para plan {plan.id}"
                    )

                    # Enviar notificación (si está configurado)
                    enviar_notificacion_orden_creada(orden, plan)

            except Exception as e:
                error_msg = f"Error procesando plan {plan.id}: {str(e)}"
                logger.error(error_msg)
                errores.append({"plan_id": plan.id, "error": str(e)})

        # Commit de todos los cambios
        db.session.commit()

        # Preparar respuesta
        resumen = {
            "fecha_ejecucion": ahora_utc.isoformat(),
            "planes_revisados": len(planes_vencidos),
            "ordenes_creadas": len(ordenes_creadas),
            "errores": len(errores),
            "detalles": {"ordenes": ordenes_creadas, "errores": errores},
        }

        logger.info(
            f"=== FIN: {len(ordenes_creadas)} órdenes creadas, {len(errores)} errores ==="
        )

        return jsonify(resumen), 200

    except Exception as e:
        logger.error(f"Error crítico en generación de órdenes: {str(e)}")
        db.session.rollback()
        return (
            jsonify({"error": "Error en generación de órdenes", "mensaje": str(e)}),
            500,
        )


def crear_orden_desde_plan(plan):
    """
    Crea una orden de trabajo a partir de un plan de mantenimiento

    Args:
        plan: PlanMantenimiento instance

    Returns:
        OrdenTrabajo: Nueva orden creada
    """
    # Generar número de orden único
    ultimo_numero = db.session.query(db.func.max(OrdenTrabajo.id)).scalar() or 0
    numero_orden = f"OT-{ultimo_numero + 1:06d}"

    # Crear descripción basada en el plan
    descripcion = f"Mantenimiento {plan.tipo_mantenimiento}: {plan.descripcion}"
    if plan.tareas:
        descripcion += f"\n\nTareas:\n{plan.tareas}"

    # Crear orden
    nueva_orden = OrdenTrabajo(
        numero_orden=numero_orden,
        tipo="Mantenimiento Preventivo",
        prioridad=plan.prioridad or "Media",
        estado="Pendiente",
        descripcion=descripcion,
        activo_id=plan.activo_id,
        tecnico_id=plan.responsable_id,
        tiempo_estimado=plan.duracion_estimada,
        fecha_programada=datetime.now(timezone.utc).date(),
        plan_mantenimiento_id=plan.id,
    )

    db.session.add(nueva_orden)

    # Actualizar próxima ejecución del plan
    plan.ultima_ejecucion = datetime.now(timezone.utc).date()

    # Calcular próxima ejecución según frecuencia
    if plan.frecuencia_dias:
        plan.proxima_ejecucion = plan.ultima_ejecucion + timedelta(
            days=plan.frecuencia_dias
        )
    elif plan.frecuencia_meses:
        # Aproximación: 1 mes = 30 días
        dias = plan.frecuencia_meses * 30
        plan.proxima_ejecucion = plan.ultima_ejecucion + timedelta(days=dias)

    return nueva_orden


def enviar_notificacion_orden_creada(orden, plan):
    """
    Envía notificación por email sobre orden creada

    Args:
        orden: OrdenTrabajo instance
        plan: PlanMantenimiento instance
    """
    try:
        # Verificar si el email está configurado
        if not current_app.config.get("MAIL_SERVER"):
            logger.info("Email no configurado, omitiendo notificación")
            return

        from flask_mail import Message, Mail

        mail = Mail(current_app)

        # Destinatarios
        destinatarios = []

        # Técnico responsable
        if orden.tecnico and orden.tecnico.email:
            destinatarios.append(orden.tecnico.email)

        # Administradores (desde configuración)
        admin_emails = current_app.config.get("ADMIN_EMAILS", "").split(",")
        destinatarios.extend([e.strip() for e in admin_emails if e.strip()])

        if not destinatarios:
            logger.warning("No hay destinatarios configurados para notificación")
            return

        # Crear mensaje
        asunto = f"Nueva Orden Preventiva: {orden.numero_orden}"

        cuerpo = f"""
Se ha generado automáticamente una nueva orden de trabajo preventivo:

ORDEN: {orden.numero_orden}
ACTIVO: {orden.activo.nombre if orden.activo else 'N/A'} ({orden.activo.codigo if orden.activo else 'N/A'})
TIPO: Mantenimiento {plan.tipo_mantenimiento}
PRIORIDAD: {orden.prioridad}
TÉCNICO ASIGNADO: {orden.tecnico.nombre if orden.tecnico else 'Sin asignar'}

DESCRIPCIÓN:
{orden.descripcion}

TIEMPO ESTIMADO: {orden.tiempo_estimado} horas
FECHA PROGRAMADA: {orden.fecha_programada.strftime('%d/%m/%Y') if orden.fecha_programada else 'No programada'}

---
Esta orden fue generada automáticamente por el sistema de mantenimiento preventivo.
Accede al sistema para más detalles: {current_app.config.get('SERVER_URL', 'http://localhost:5000')}
"""

        msg = Message(subject=asunto, recipients=destinatarios, body=cuerpo)

        mail.send(msg)
        logger.info(f"Notificación enviada a: {', '.join(destinatarios)}")

    except Exception as e:
        logger.error(f"Error enviando notificación: {str(e)}")
        # No fallar si el email falla


@cron_bp.route("/verificar-alertas", methods=["GET", "POST"])
def verificar_alertas():
    """
    Verifica activos sin mantenimiento reciente y envía alertas

    Ejecutado por Cloud Scheduler semanalmente
    """
    if not is_valid_cron_request():
        return jsonify({"error": "Acceso no autorizado"}), 403

    try:
        logger.info("=== INICIO: Verificación de alertas ===")

        # Fecha límite (activos sin mantenimiento en últimos 90 días)
        fecha_limite = datetime.now(timezone.utc).date() - timedelta(days=90)

        # Buscar activos críticos sin órdenes recientes
        from sqlalchemy import or_

        activos_sin_mantenimiento = Activo.query.filter(
            and_(
                Activo.estado.in_(["Operativo", "En Mantenimiento"]),
                or_(
                    Activo.fecha_ultimo_mantenimiento == None,
                    Activo.fecha_ultimo_mantenimiento < fecha_limite,
                ),
            )
        ).all()

        alertas_enviadas = []

        for activo in activos_sin_mantenimiento:
            # Enviar alerta
            enviar_alerta_mantenimiento(activo)
            alertas_enviadas.append(
                {
                    "activo_id": activo.id,
                    "codigo": activo.codigo,
                    "nombre": activo.nombre,
                    "ultimo_mantenimiento": (
                        activo.fecha_ultimo_mantenimiento.isoformat()
                        if activo.fecha_ultimo_mantenimiento
                        else None
                    ),
                }
            )

        logger.info(f"=== FIN: {len(alertas_enviadas)} alertas enviadas ===")

        return (
            jsonify(
                {
                    "fecha": datetime.now(timezone.utc).isoformat(),
                    "activos_revisados": Activo.query.count(),
                    "alertas_enviadas": len(alertas_enviadas),
                    "detalles": alertas_enviadas,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error en verificación de alertas: {str(e)}")
        return jsonify({"error": str(e)}), 500


def enviar_alerta_mantenimiento(activo):
    """Envía alerta sobre activo que requiere mantenimiento"""
    try:
        if not current_app.config.get("MAIL_SERVER"):
            return

        from flask_mail import Message, Mail

        mail = Mail(current_app)

        admin_emails = current_app.config.get("ADMIN_EMAILS", "").split(",")
        destinatarios = [e.strip() for e in admin_emails if e.strip()]

        if not destinatarios:
            return

        msg = Message(
            subject=f"⚠️ Alerta: {activo.nombre} requiere mantenimiento",
            recipients=destinatarios,
            body=f"""
ALERTA DE MANTENIMIENTO

ACTIVO: {activo.nombre} ({activo.codigo})
UBICACIÓN: {activo.ubicacion or 'No especificada'}
ÚLTIMO MANTENIMIENTO: {activo.fecha_ultimo_mantenimiento.strftime('%d/%m/%Y') if activo.fecha_ultimo_mantenimiento else 'Nunca'}

Este activo lleva más de 90 días sin mantenimiento registrado.
Se recomienda programar una inspección o mantenimiento preventivo.

Accede al sistema: {current_app.config.get('SERVER_URL', 'http://localhost:5000')}
""",
        )

        mail.send(msg)
        logger.info(f"Alerta enviada para activo {activo.codigo}")

    except Exception as e:
        logger.error(f"Error enviando alerta para activo {activo.id}: {str(e)}")


@cron_bp.route("/test", methods=["GET"])
def test_cron():
    """
    Endpoint de prueba para verificar que el cron funciona
    Solo en desarrollo
    """
    if current_app.config.get("FLASK_ENV") != "development":
        return jsonify({"error": "Solo disponible en desarrollo"}), 403

    return (
        jsonify(
            {
                "mensaje": "Endpoint de cron funcionando",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cron_header": request.headers.get("X-Appengine-Cron", "No presente"),
            }
        ),
        200,
    )
