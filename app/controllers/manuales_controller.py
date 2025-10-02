"""
Controlador para gestionar manuales de activos
"""

import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import send_file, jsonify, current_app, redirect
from app.models.manual import Manual
from app.models.activo import Activo
from app.extensions import db
from app.utils.storage import upload_file, delete_file, get_signed_url


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

        # Nombre único basado en código del activo
        codigo_activo = (
            secure_filename(activo.codigo) if activo.codigo else f"ACT{activo_id}"
        )
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{codigo_activo}_{tipo}_{timestamp}.{extension}"

        # Subir archivo a Cloud Storage (o local en desarrollo)
        file_url = upload_file(archivo, "manuales", unique_filename)

        if not file_url:
            raise Exception("Error al subir el archivo")

        # Crear registro en base de datos
        manual = Manual(
            activo_id=activo_id,
            nombre_archivo=filename,
            nombre_unico=unique_filename,
            tipo=tipo,
            descripcion=descripcion,
            ruta_archivo=file_url,  # Ahora es URL de GCS o path local
            tamano=size,
            extension=extension,
            fecha_subida=datetime.utcnow(),
        )

        db.session.add(manual)
        db.session.commit()

        return manual.to_dict()

    except Exception as e:
        db.session.rollback()
        # Si hubo error, intentar eliminar archivo
        if "file_url" in locals() and file_url:
            try:
                delete_file(file_url, "manuales")
            except:
                pass  # Ignorar errores de limpieza
        raise Exception(f"Error al crear manual: {str(e)}")


def descargar_manual_archivo(manual_id):
    """Descargar un archivo de manual"""
    try:
        manual = Manual.query.get(manual_id)
        if not manual:
            raise Exception("Manual no encontrado")

        # Si es GCS, generar URL firmada y redirigir
        if manual.ruta_archivo.startswith("gs://"):
            url = get_signed_url(
                manual.ruta_archivo, "manuales", expiration=300
            )  # 5 min
            return redirect(url)

        # Si es local, verificar existencia y enviar
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

        # Solo permitir previsualización de ciertos tipos
        if manual.extension.lower() not in ["pdf", "png", "jpg", "jpeg"]:
            raise Exception("Tipo de archivo no soportado para previsualización")

        # Si es GCS, generar URL firmada y redirigir
        if manual.ruta_archivo.startswith("gs://"):
            url = get_signed_url(
                manual.ruta_archivo, "manuales", expiration=3600
            )  # 1 hora
            return redirect(url)

        # Si es local, verificar y enviar
        if not os.path.exists(manual.ruta_archivo):
            raise Exception("Archivo no encontrado en el servidor")

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

        # Eliminar archivo (de GCS o local)
        if manual.ruta_archivo:
            delete_file(manual.ruta_archivo, "manuales")

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
