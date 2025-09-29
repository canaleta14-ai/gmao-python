"""
Controlador para gestionar manuales de activos
"""

import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import send_file, jsonify, current_app
from app.models.manual import Manual
from app.models.activo import Activo
from app.extensions import db


# Extensiones permitidas
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt", "png", "jpg", "jpeg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename):
    """Verificar si la extensión del archivo está permitida"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def obtener_manuales_activo(activo_id):
    """Obtener todos los manuales de un activo"""
    try:
        manuales = Manual.query.filter_by(activo_id=activo_id).all()
        return [manual.to_dict() for manual in manuales]
    except Exception as e:
        raise Exception(f"Error al obtener manuales: {str(e)}")


def crear_manual(activo_id, archivo, tipo, descripcion):
    """Crear un nuevo manual para un activo"""
    try:
        # Verificar que el activo existe
        activo = Activo.query.get(activo_id)
        if not activo:
            raise Exception("El activo no existe")

        # Verificar archivo
        if not archivo or archivo.filename == "":
            raise Exception("No se seleccionó ningún archivo")

        if not allowed_file(archivo.filename):
            raise Exception("Tipo de archivo no permitido")

        # Verificar tamaño
        archivo.seek(0, 2)  # Ir al final del archivo
        size = archivo.tell()
        archivo.seek(0)  # Volver al inicio

        if size > MAX_FILE_SIZE:
            raise Exception("El archivo supera el tamaño máximo permitido (5MB)")

        # Generar nombre único para el archivo
        filename = secure_filename(archivo.filename)
        extension = filename.rsplit(".", 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{extension}"

        # Crear directorio si no existe
        upload_folder = os.path.join(
            current_app.config.get("UPLOAD_FOLDER", "uploads"), "manuales"
        )
        os.makedirs(upload_folder, exist_ok=True)

        # Guardar archivo
        file_path = os.path.join(upload_folder, unique_filename)
        archivo.save(file_path)

        # Crear registro en base de datos
        manual = Manual(
            activo_id=activo_id,
            nombre_archivo=filename,
            nombre_unico=unique_filename,
            tipo=tipo,
            descripcion=descripcion,
            ruta_archivo=file_path,
            tamano=size,
            extension=extension,
            fecha_subida=datetime.utcnow(),
        )

        db.session.add(manual)
        db.session.commit()

        return manual.to_dict()

    except Exception as e:
        db.session.rollback()
        # Eliminar archivo si se creó
        if "file_path" in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise Exception(f"Error al crear manual: {str(e)}")


def descargar_manual_archivo(manual_id):
    """Descargar un archivo de manual"""
    try:
        manual = Manual.query.get(manual_id)
        if not manual:
            raise Exception("Manual no encontrado")

        if not os.path.exists(manual.ruta_archivo):
            raise Exception("Archivo no encontrado en el servidor")

        return send_file(
            manual.ruta_archivo,
            as_attachment=True,
            download_name=manual.nombre_archivo,
            mimetype="application/octet-stream",
        )

    except Exception as e:
        raise Exception(f"Error al descargar manual: {str(e)}")


def previsualizar_manual_archivo(manual_id):
    """Previsualizar un archivo de manual (para PDFs e imágenes)"""
    try:
        manual = Manual.query.get(manual_id)
        if not manual:
            raise Exception("Manual no encontrado")

        if not os.path.exists(manual.ruta_archivo):
            raise Exception("Archivo no encontrado en el servidor")

        # Solo permitir previsualización de ciertos tipos
        if manual.extension.lower() not in ["pdf", "png", "jpg", "jpeg"]:
            raise Exception("Tipo de archivo no soportado para previsualización")

        # Determinar mimetype
        mimetypes = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
        }

        mimetype = mimetypes.get(manual.extension.lower(), "application/octet-stream")

        return send_file(manual.ruta_archivo, mimetype=mimetype, as_attachment=False)

    except Exception as e:
        raise Exception(f"Error al previsualizar manual: {str(e)}")


def eliminar_manual_archivo(manual_id):
    """Eliminar un manual y su archivo"""
    try:
        manual = Manual.query.get(manual_id)
        if not manual:
            raise Exception("Manual no encontrado")

        # Eliminar archivo físico
        if os.path.exists(manual.ruta_archivo):
            os.remove(manual.ruta_archivo)

        # Eliminar registro de base de datos
        db.session.delete(manual)
        db.session.commit()

        return {"mensaje": "Manual eliminado exitosamente"}

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error al eliminar manual: {str(e)}")


def obtener_manual_por_id(manual_id):
    """Obtener un manual por su ID"""
    try:
        manual = Manual.query.get(manual_id)
        if not manual:
            raise Exception("Manual no encontrado")

        return manual.to_dict()

    except Exception as e:
        raise Exception(f"Error al obtener manual: {str(e)}")
