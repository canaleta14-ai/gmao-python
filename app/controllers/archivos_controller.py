import os
import uuid
from datetime import datetime
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
from flask import request, current_app
from app.extensions import db
from app.models import ArchivoAdjunto, OrdenTrabajo


def subir_archivo(orden_id, usuario_id):
    """Subir archivo adjunto a una orden de trabajo"""

    # Verificar que la orden existe
    orden = OrdenTrabajo.query.get_or_404(orden_id)

    # Verificar si hay archivo en la request
    if "archivo" not in request.files:
        raise ValueError("No se encontró archivo en la solicitud")

    archivo = request.files["archivo"]

    if archivo.filename == "":
        raise ValueError("No se seleccionó ningún archivo")

    if archivo and _archivo_permitido(archivo.filename):
        # Generar nombre único para el archivo
        nombre_original = secure_filename(archivo.filename)
        extension = _obtener_extension(nombre_original)
        nombre_unico = f"{uuid.uuid4().hex}{extension}"

        # Crear directorio si no existe
        upload_dir = os.path.join(current_app.static_folder, "uploads", "ordenes")
        os.makedirs(upload_dir, exist_ok=True)

        # Guardar archivo
        ruta_archivo = os.path.join(upload_dir, nombre_unico)
        archivo.save(ruta_archivo)

        # Determinar tipo de archivo
        tipo_archivo = _determinar_tipo_archivo(extension)

        # Obtener descripción si se proporcionó
        descripcion = request.form.get("descripcion", "")

        # Crear registro en base de datos
        archivo_adjunto = ArchivoAdjunto(
            nombre_original=nombre_original,
            nombre_archivo=nombre_unico,
            tipo_archivo=tipo_archivo,
            extension=extension,
            tamaño=os.path.getsize(ruta_archivo),
            ruta_archivo=f"uploads/ordenes/{nombre_unico}",
            descripcion=descripcion,
            orden_trabajo_id=orden_id,
            usuario_id=usuario_id,
        )

        db.session.add(archivo_adjunto)
        db.session.commit()

        return {
            "id": archivo_adjunto.id,
            "mensaje": "Archivo subido exitosamente",
            "archivo": archivo_adjunto.to_dict(),
        }

    else:
        raise ValueError("Tipo de archivo no permitido")


def agregar_enlace(orden_id, data, usuario_id):
    """Agregar enlace externo a una orden de trabajo"""

    # Verificar que la orden existe
    orden = OrdenTrabajo.query.get_or_404(orden_id)

    url = data.get("url")
    descripcion = data.get("descripcion", "")

    # Validar URL
    if not _validar_url(url):
        raise ValueError("URL no válida")

    # Crear registro en base de datos
    enlace = ArchivoAdjunto(
        nombre_original=f"Enlace: {url}",
        nombre_archivo="",
        tipo_archivo="enlace",
        url_enlace=url,
        descripcion=descripcion,
        orden_trabajo_id=orden_id,
        usuario_id=usuario_id,
    )

    db.session.add(enlace)
    db.session.commit()

    return {
        "id": enlace.id,
        "mensaje": "Enlace agregado exitosamente",
        "enlace": enlace.to_dict(),
    }


def listar_archivos_orden(orden_id):
    """Obtener lista de archivos adjuntos de una orden"""

    # Verificar que la orden existe
    orden = OrdenTrabajo.query.get_or_404(orden_id)

    archivos = ArchivoAdjunto.query.filter_by(orden_trabajo_id=orden_id).all()

    return [archivo.to_dict() for archivo in archivos]


def eliminar_archivo(archivo_id):
    """Eliminar archivo adjunto"""

    archivo = ArchivoAdjunto.query.get_or_404(archivo_id)

    # Eliminar archivo físico si existe
    if archivo.ruta_archivo and archivo.tipo_archivo != "enlace":
        ruta_completa = os.path.join(current_app.static_folder, archivo.ruta_archivo)
        if os.path.exists(ruta_completa):
            os.remove(ruta_completa)

    # Eliminar registro de base de datos
    db.session.delete(archivo)
    db.session.commit()


def descargar_archivo(archivo_id):
    """Obtener ruta de archivo para descarga"""

    archivo = ArchivoAdjunto.query.get_or_404(archivo_id)

    if archivo.tipo_archivo == "enlace":
        raise ValueError("Los enlaces no se pueden descargar")

    ruta_completa = os.path.join(current_app.static_folder, archivo.ruta_archivo)

    if not os.path.exists(ruta_completa):
        raise ValueError("Archivo no encontrado en el servidor")

    return ruta_completa, archivo.nombre_original


def _archivo_permitido(filename):
    """Verificar si el tipo de archivo está permitido"""
    EXTENSIONES_PERMITIDAS = {
        # Imágenes
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".webp",
        ".svg",
        # Documentos
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".txt",
        ".csv",
        ".rtf",
        ".odt",
        ".ods",
        ".odp",
        # Otros
        ".zip",
        ".rar",
        ".7z",
        ".tar.gz",
    }

    extension = _obtener_extension(filename)
    return extension.lower() in EXTENSIONES_PERMITIDAS


def _obtener_extension(filename):
    """Obtener extensión del archivo"""
    return os.path.splitext(filename)[1]


def _determinar_tipo_archivo(extension):
    """Determinar tipo de archivo basado en extensión"""
    extension = extension.lower()

    if extension in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"]:
        return "imagen"
    elif extension in [
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".txt",
        ".csv",
        ".rtf",
        ".odt",
        ".ods",
        ".odp",
    ]:
        return "documento"
    else:
        return "archivo"


def _validar_url(url):
    """Validar formato de URL"""
    try:
        resultado = urlparse(url)
        return all([resultado.scheme, resultado.netloc])
    except:
        return False
