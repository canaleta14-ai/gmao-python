from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app.extensions import db
from app.models.solicitud_servicio import SolicitudServicio
from datetime import datetime
import re
import os

# Importar utilidades de email
from app.utils.email_utils import (
    enviar_email_confirmacion,
    enviar_email_notificacion_admin,
)

solicitudes_bp = Blueprint("solicitudes", __name__, url_prefix="/solicitudes")


@solicitudes_bp.route("/", methods=["GET", "POST"])
def nueva_solicitud():
    """Página pública para crear nuevas solicitudes de servicio"""
    if request.method == "POST":
        return procesar_solicitud()

    return render_template("solicitudes/nueva_solicitud.html")


@solicitudes_bp.route("/procesar", methods=["POST"])
def procesar_solicitud():
    """Procesa el formulario de solicitud de servicio"""
    try:
        # Validar datos del formulario
        datos = validar_datos_solicitud(request.form)

        if not datos["valido"]:
            flash("Por favor corrija los errores en el formulario.", "error")
            return render_template(
                "solicitudes/nueva_solicitud.html",
                errores=datos["errores"],
                datos_form=request.form,
            )

        # Generar número de solicitud único
        numero_solicitud = generar_numero_solicitud()

        # Crear la solicitud
        solicitud = SolicitudServicio(
            numero_solicitud=numero_solicitud,
            nombre_solicitante=datos["datos"]["nombre_solicitante"],
            email_solicitante=datos["datos"]["email_solicitante"],
            telefono_solicitante=datos["datos"]["telefono_solicitante"],
            empresa_solicitante=datos["datos"]["empresa_solicitante"],
            tipo_servicio=datos["datos"]["tipo_servicio"],
            prioridad=datos["datos"]["prioridad"],
            titulo=datos["datos"]["titulo"],
            descripcion=datos["datos"]["descripcion"],
            ubicacion=datos["datos"]["ubicacion"],
            activo_afectado=datos["datos"]["activo_afectado"],
        )

        # Guardar en base de datos
        db.session.add(solicitud)
        db.session.commit()

        # Enviar emails de confirmación
        try:
            enviar_email_confirmacion(solicitud)
            enviar_email_notificacion_admin(solicitud)
        except Exception as e:
            print(f"Error enviando emails: {e}")
            # No fallar la solicitud por error de email

        flash(
            "Su solicitud ha sido enviada exitosamente. Recibirá una confirmación por email.",
            "success",
        )
        return redirect(url_for("solicitudes.confirmacion", numero=numero_solicitud))

    except Exception as e:
        db.session.rollback()
        print(f"Error procesando solicitud: {e}")
        flash(
            "Ha ocurrido un error al procesar su solicitud. Por favor, inténtelo nuevamente.",
            "error",
        )
        return render_template(
            "solicitudes/nueva_solicitud.html",
            errores=["Error interno del servidor"],
            datos_form=request.form,
        )


@solicitudes_bp.route("/confirmacion/<numero>")
def confirmacion(numero):
    """Página de confirmación de solicitud enviada"""
    solicitud = SolicitudServicio.query.filter_by(numero_solicitud=numero).first()

    if not solicitud:
        flash("Solicitud no encontrada.", "error")
        return redirect(url_for("solicitudes.nueva_solicitud"))

    return render_template("solicitudes/confirmacion.html", solicitud=solicitud)


@solicitudes_bp.route("/seguimiento/<numero>")
def seguimiento(numero):
    """Página pública para seguimiento de solicitud"""
    solicitud = SolicitudServicio.query.filter_by(numero_solicitud=numero).first()

    if not solicitud:
        flash("Solicitud no encontrada.", "error")
        return redirect(url_for("solicitudes.nueva_solicitud"))

    return render_template("solicitudes/seguimiento.html", solicitud=solicitud)


@solicitudes_bp.route("/api/seguimiento/<numero>")
def api_seguimiento(numero):
    """API para consultar estado de solicitud"""
    solicitud = SolicitudServicio.query.filter_by(numero_solicitud=numero).first()

    if not solicitud:
        return jsonify({"error": "Solicitud no encontrada"}), 404

    return jsonify(
        {
            "numero_solicitud": solicitud.numero_solicitud,
            "estado": solicitud.estado,
            "estado_display": solicitud.estado_display,
            "fecha_creacion": (
                solicitud.fecha_creacion.isoformat()
                if solicitud.fecha_creacion
                else None
            ),
            "fecha_actualizacion": (
                solicitud.fecha_actualizacion.isoformat()
                if solicitud.fecha_actualizacion
                else None
            ),
            "titulo": solicitud.titulo,
            "tipo_servicio": solicitud.tipo_servicio_display,
            "prioridad": solicitud.prioridad_display,
        }
    )


def validar_datos_solicitud(form_data):
    """Valida los datos del formulario de solicitud"""
    errores = []
    datos = {}

    # Campos requeridos
    campos_requeridos = {
        "nombre_solicitante": "Nombre del solicitante",
        "email_solicitante": "Email",
        "tipo_servicio": "Tipo de servicio",
        "titulo": "Título",
        "descripcion": "Descripción",
    }

    for campo, nombre in campos_requeridos.items():
        valor = form_data.get(campo, "").strip()
        if not valor:
            errores.append(f"{nombre} es requerido.")
        datos[campo] = valor

    # Validar email
    if datos.get("email_solicitante"):
        if not re.match(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            datos["email_solicitante"],
        ):
            errores.append("El email no tiene un formato válido.")

    # Validar teléfono (opcional pero si se proporciona debe ser válido)
    telefono = form_data.get("telefono_solicitante", "").strip()
    if telefono and not re.match(r"^[\d\s\-\+\(\)]{7,20}$", telefono):
        errores.append("El teléfono no tiene un formato válido.")
    datos["telefono_solicitante"] = telefono

    # Campos opcionales
    datos["empresa_solicitante"] = form_data.get("empresa_solicitante", "").strip()
    datos["ubicacion"] = form_data.get("ubicacion", "").strip()
    datos["activo_afectado"] = form_data.get("activo_afectado", "").strip()

    # Validar tipo de servicio
    tipos_validos = ["mantenimiento", "reparacion", "instalacion", "otro"]
    if datos.get("tipo_servicio") and datos["tipo_servicio"] not in tipos_validos:
        errores.append("Tipo de servicio no válido.")
        datos["tipo_servicio"] = "otro"

    # Validar prioridad
    prioridades_validas = ["baja", "normal", "alta", "urgente"]
    prioridad = form_data.get("prioridad", "normal")
    if prioridad not in prioridades_validas:
        prioridad = "normal"
    datos["prioridad"] = prioridad

    return {"valido": len(errores) == 0, "errores": errores, "datos": datos}


def generar_numero_solicitud():
    """Genera un número único para la solicitud"""
    # Formato: SOL-YYYY-NNNN (ej: SOL-2025-0001)
    año_actual = datetime.now().year

    # Buscar el último número del año
    ultima_solicitud = (
        SolicitudServicio.query.filter(
            SolicitudServicio.numero_solicitud.like(f"SOL-{año_actual}-%")
        )
        .order_by(SolicitudServicio.id.desc())
        .first()
    )

    if ultima_solicitud:
        # Extraer el número secuencial
        partes = ultima_solicitud.numero_solicitud.split("-")
        if len(partes) == 3:
            numero_secuencial = int(partes[2]) + 1
        else:
            numero_secuencial = 1
    else:
        numero_secuencial = 1

    return f"SOL-{año_actual}-{numero_secuencial:04d}"
