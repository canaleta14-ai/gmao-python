from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    jsonify,
    send_file,
)
from app.extensions import db
from app.models.solicitud_servicio import SolicitudServicio
from app.models.archivo_adjunto import ArchivoAdjunto
from datetime import datetime
import re
import os
from werkzeug.utils import secure_filename
import uuid

# Importar utilidades de email
from app.utils.email_utils import (
    enviar_email_confirmacion,
    enviar_email_notificacion_admin,
)
from app.utils.storage import (
    upload_file,
    is_gcp_environment,
    get_signed_url,
    file_exists,
)

solicitudes_bp = Blueprint("solicitudes", __name__, url_prefix="/solicitudes")

# Configuración de archivos permitidos
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "doc", "docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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
        db.session.flush()  # Para obtener el ID de la solicitud

        # Procesar archivos adjuntos
        archivos_guardados = 0
        if "archivos" in request.files:
            archivos = request.files.getlist("archivos")
            archivos_guardados = procesar_archivos_solicitud(archivos, solicitud.id)

        db.session.commit()

        # Enviar emails de confirmación
        try:
            enviar_email_confirmacion(solicitud)
            enviar_email_notificacion_admin(solicitud)
        except Exception as e:
            current_app.logger.error(f"Error enviando emails: {e}")
            # No fallar la solicitud por error de email

        mensaje = f"Su solicitud ha sido enviada exitosamente."
        if archivos_guardados > 0:
            mensaje += f" Se adjuntaron {archivos_guardados} archivo(s)."
        mensaje += " Recibirá una confirmación por email."

        flash(mensaje, "success")
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


def procesar_archivos_solicitud(archivos, solicitud_id):
    """
    Procesa y guarda archivos adjuntos para una solicitud de servicio
    Guarda archivos en el filesystem local

    Args:
        archivos: Lista de archivos desde request.files.getlist()
        solicitud_id: ID de la solicitud de servicio

    Returns:
        Número de archivos guardados exitosamente
    """
    archivos_guardados = 0

    for archivo in archivos:
        # Validar que el archivo existe y tiene contenido
        if not archivo or archivo.filename == "":
            continue

        # Validar extensión permitida
        if not allowed_file(archivo.filename):
            print(f"Archivo rechazado (extensión no permitida): {archivo.filename}")
            continue

        # Validar tamaño
        archivo.seek(0, os.SEEK_END)
        file_length = archivo.tell()
        archivo.seek(0)

        if file_length > MAX_FILE_SIZE:
            print(
                f"Archivo rechazado (tamaño excedido): {archivo.filename} ({file_length} bytes)"
            )
            continue

        try:
            # Generar nombre único para el archivo
            filename = secure_filename(archivo.filename)
            nombre_unico = f"{uuid.uuid4().hex[:8]}_{filename}"

            # Guardar archivo en el filesystem local
            folder = f"solicitudes/{solicitud_id}"
            ruta_archivo = upload_file(archivo, folder, nombre_unico)

            if not ruta_archivo:
                print(f"Error subiendo archivo {archivo.filename}")
                continue

            # Obtener información del archivo
            extension = filename.rsplit(".", 1)[1].lower() if "." in filename else ""

            # Determinar tipo de archivo
            if extension in ["jpg", "jpeg", "png", "gif"]:
                tipo_archivo = "imagen"
            elif extension == "pdf":
                tipo_archivo = "documento"
            else:
                tipo_archivo = "documento"

            # Crear registro en base de datos
            archivo_adjunto = ArchivoAdjunto(
                nombre_original=filename,
                nombre_archivo=nombre_unico,
                tipo_archivo=tipo_archivo,
                extension=extension,
                tamaño=file_length,
                ruta_archivo=ruta_archivo,  # Ahora puede ser URL de GCS o path local
                solicitud_servicio_id=solicitud_id,
                usuario_id=None,  # Las solicitudes públicas no tienen usuario
            )

            db.session.add(archivo_adjunto)
            archivos_guardados += 1

        except Exception as e:
            print(f"Error guardando archivo {archivo.filename}: {e}")
            continue

    return archivos_guardados


@solicitudes_bp.route("/api/archivos/<int:archivo_id>/download", methods=["GET"])
def descargar_archivo_adjunto(archivo_id):
    """Descargar archivo adjunto de solicitud"""
    try:
        # Buscar el archivo en la base de datos
        archivo = ArchivoAdjunto.query.get_or_404(archivo_id)

        # Verificar que es un archivo (no un enlace)
        if archivo.tipo_archivo == "enlace":
            return jsonify({"error": "Los enlaces no se pueden descargar"}), 400

        # Verificar que el archivo existe en el filesystem local
        if not os.path.exists(archivo.ruta_archivo):
            return jsonify({"error": "Archivo no encontrado en el servidor"}), 404

        return send_file(
            archivo.ruta_archivo,
            as_attachment=True,
            download_name=archivo.nombre_original,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 400
