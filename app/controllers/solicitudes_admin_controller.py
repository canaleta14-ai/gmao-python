from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.solicitud_servicio import SolicitudServicio
from app.models.usuario import Usuario
from app.utils.email_utils import enviar_email
from datetime import datetime
import os

# Crear blueprint para gestión administrativa de solicitudes
solicitudes_admin_bp = Blueprint(
    "solicitudes_admin", __name__, url_prefix="/admin/solicitudes"
)


@solicitudes_admin_bp.route("/", methods=["GET"])
@login_required
def listar_solicitudes():
    """Lista todas las solicitudes para administración"""
    # Solo administradores pueden acceder
    if current_user.rol != "Administrador":
        flash("No tiene permisos para acceder a esta sección.", "error")
        return redirect(url_for("web.index"))

    # Obtener filtros
    estado = request.args.get("estado", "todos")
    tipo = request.args.get("tipo", "todos")
    page = int(request.args.get("page", 1))
    per_page = 25

    # Construir query
    query = SolicitudServicio.query

    if estado != "todos":
        query = query.filter_by(estado=estado)

    if tipo != "todos":
        query = query.filter_by(tipo_servicio=tipo)

    # Ordenar por fecha de creación (más recientes primero)
    query = query.order_by(SolicitudServicio.fecha_creacion.desc())

    # Paginación
    solicitudes = query.paginate(page=page, per_page=per_page, error_out=False)

    # Calcular estadísticas
    estadisticas = {
        "total_pendientes": SolicitudServicio.query.filter_by(
            estado="pendiente"
        ).count(),
        "total_revision": SolicitudServicio.query.filter_by(
            estado="en_revision"
        ).count(),
        "total_progreso": SolicitudServicio.query.filter_by(
            estado="en_progreso"
        ).count(),
        "total_completadas": SolicitudServicio.query.filter_by(
            estado="completada"
        ).count(),
    }

    return render_template(
        "admin/solicitudes/listar.html",
        solicitudes=solicitudes,
        estadisticas=estadisticas,
        estado=estado,
        tipo=tipo,
        total_paginas=solicitudes.pages,
    )


@solicitudes_admin_bp.route("/<int:id>", methods=["GET"])
@login_required
def ver_solicitud(id):
    """Ver detalles de una solicitud específica"""
    if current_user.rol != "Administrador":
        flash("No tiene permisos para acceder a esta sección.", "error")
        return redirect(url_for("web.index"))

    solicitud = SolicitudServicio.query.get_or_404(id)

    return render_template("admin/solicitudes/ver.html", solicitud=solicitud)


@solicitudes_admin_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar_solicitud(id):
    """Editar una solicitud específica"""
    if current_user.rol != "Administrador":
        flash("No tiene permisos para acceder a esta sección.", "error")
        return redirect(url_for("web.index"))

    solicitud = SolicitudServicio.query.get_or_404(id)

    if request.method == "POST":
        # Procesar el formulario de edición
        try:
            # Actualizar campos editables
            solicitud.titulo = request.form.get("titulo", solicitud.titulo)
            solicitud.descripcion = request.form.get(
                "descripcion", solicitud.descripcion
            )
            solicitud.tipo_servicio = request.form.get(
                "tipo_servicio", solicitud.tipo_servicio
            )
            solicitud.prioridad = request.form.get("prioridad", solicitud.prioridad)
            solicitud.fecha_actualizacion = datetime.utcnow()

            db.session.commit()

            flash("Solicitud actualizada correctamente.", "success")
            return redirect(url_for("solicitudes_admin.ver_solicitud", id=solicitud.id))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar la solicitud: {str(e)}", "error")

    return render_template("admin/solicitudes/editar.html", solicitud=solicitud)


@solicitudes_admin_bp.route("/<int:id>/estado", methods=["POST"])
@login_required
def cambiar_estado(id):
    """Cambiar el estado de una solicitud"""
    if current_user.rol != "Administrador":
        return jsonify({"error": "No autorizado"}), 403

    solicitud = SolicitudServicio.query.get_or_404(id)

    # Manejar tanto datos de formulario como JSON
    if request.is_json:
        data = request.get_json()
        nuevo_estado = data.get("estado")
        observaciones = data.get("comentario", "")  # Los templates usan "comentario"
    else:
        nuevo_estado = request.form.get("estado")
        observaciones = request.form.get("observaciones", "")

    if nuevo_estado not in [
        "pendiente",
        "en_revision",
        "aprobada",
        "rechazada",
        "en_progreso",
        "completada",
        "cancelada",
    ]:
        return jsonify({"error": "Estado no válido"}), 400

    estado_anterior = solicitud.estado
    solicitud.estado = nuevo_estado
    solicitud.fecha_actualizacion = datetime.utcnow()

    if observaciones:
        solicitud.observaciones_internas = observaciones

    try:
        db.session.commit()

        # Enviar notificación por email al solicitante
        enviar_notificacion_estado(solicitud, estado_anterior)

        return jsonify(
            {
                "success": True,
                "mensaje": f"Estado cambiado a {solicitud.estado_display}",
                "estado": solicitud.estado,
                "estado_display": solicitud.estado_display,
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@solicitudes_admin_bp.route("/<int:id>/asignar", methods=["POST"])
@login_required
def asignar_solicitud(id):
    """Asignar una solicitud a un técnico"""
    if current_user.rol != "Administrador":
        return jsonify({"error": "No autorizado"}), 403

    solicitud = SolicitudServicio.query.get_or_404(id)

    tecnico_id = request.form.get("tecnico_id")
    if tecnico_id:
        tecnico = Usuario.query.get(int(tecnico_id))
        if tecnico and tecnico.rol in ["Administrador", "Técnico"]:
            solicitud.asignado_a_id = int(tecnico_id)
        else:
            return jsonify({"error": "Técnico no válido"}), 400
    else:
        solicitud.asignado_a_id = None

    solicitud.fecha_actualizacion = datetime.utcnow()

    try:
        db.session.commit()
        return jsonify(
            {
                "success": True,
                "mensaje": "Solicitud asignada correctamente",
                "asignado_a": (
                    solicitud.asignado_a.nombre if solicitud.asignado_a else None
                ),
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@solicitudes_admin_bp.route("/api/estadisticas")
@login_required
def api_estadisticas():
    """API para obtener estadísticas de solicitudes"""
    if current_user.rol != "Administrador":
        return jsonify({"error": "No autorizado"}), 403

    # Estadísticas generales
    total = SolicitudServicio.query.count()
    pendientes = SolicitudServicio.query.filter_by(estado="pendiente").count()
    en_progreso = SolicitudServicio.query.filter_by(estado="en_progreso").count()
    completadas = SolicitudServicio.query.filter_by(estado="completada").count()

    # Por tipo de servicio
    tipos = (
        db.session.query(
            SolicitudServicio.tipo_servicio,
            db.func.count(SolicitudServicio.id).label("cantidad"),
        )
        .group_by(SolicitudServicio.tipo_servicio)
        .all()
    )

    # Por prioridad
    prioridades = (
        db.session.query(
            SolicitudServicio.prioridad,
            db.func.count(SolicitudServicio.id).label("cantidad"),
        )
        .group_by(SolicitudServicio.prioridad)
        .all()
    )

    return jsonify(
        {
            "total": total,
            "pendientes": pendientes,
            "en_progreso": en_progreso,
            "completadas": completadas,
            "tipos": [{"tipo": t[0], "cantidad": t[1]} for t in tipos],
            "prioridades": [{"prioridad": p[0], "cantidad": p[1]} for p in prioridades],
        }
    )


def enviar_notificacion_estado(solicitud, estado_anterior):
    """Enviar notificación por email cuando cambia el estado"""
    try:
        asunto = f"Actualización de Solicitud #{solicitud.numero_solicitud} - GMAO"

        contenido_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">Actualización de Estado de Solicitud</h2>

            <p>Estimado/a {solicitud.nombre_solicitante},</p>

            <p>Le informamos que el estado de su solicitud ha sido actualizado:</p>

            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3>Detalles de la Solicitud</h3>
                <p><strong>Número de Solicitud:</strong> {solicitud.numero_solicitud}</p>
                <p><strong>Título:</strong> {solicitud.titulo}</p>
                <p><strong>Estado Anterior:</strong> {SolicitudServicio(estado=estado_anterior).estado_display}</p>
                <p><strong>Nuevo Estado:</strong> <span style="color: #0d6efd; font-weight: bold;">{solicitud.estado_display}</span></p>
                <p><strong>Fecha de Actualización:</strong> {solicitud.fecha_actualizacion.strftime('%d/%m/%Y %H:%M')}</p>
            </div>

            <div style="background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h4>¿Qué significa este estado?</h4>
                <ul>
                    <li><strong>Pendiente:</strong> Su solicitud ha sido recibida y está esperando revisión</li>
                    <li><strong>En Revisión:</strong> Estamos evaluando su solicitud</li>
                    <li><strong>Aprobada:</strong> Su solicitud ha sido aprobada y será atendida pronto</li>
                    <li><strong>En Progreso:</strong> Estamos trabajando en su solicitud</li>
                    <li><strong>Completada:</strong> Su solicitud ha sido finalizada exitosamente</li>
                </ul>
            </div>

            <p>Puede hacer seguimiento de su solicitud visitando:</p>
            <p><a href="{request.host_url}solicitudes/seguimiento/{solicitud.numero_solicitud}"
                  style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Ver Estado de la Solicitud
            </a></p>

            <p>Si tiene alguna pregunta, no dude en contactarnos.</p>

            <p>Atentamente,<br>
            Equipo de Mantenimiento GMAO</p>
        </div>
        """

        enviar_email(solicitud.email_solicitante, asunto, contenido_html)

    except Exception as e:
        print(f"Error enviando notificación de estado: {e}")
        # No fallar la operación por error de email
