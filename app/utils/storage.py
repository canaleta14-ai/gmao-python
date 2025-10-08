"""
Utilidades para Google Cloud Storage
Maneja persistencia de archivos en GCP y local
"""

import os
import logging
from werkzeug.utils import secure_filename
from datetime import timedelta

logger = logging.getLogger(__name__)

# Configuración
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "gmao-uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def get_storage_client():
    """
    Obtiene cliente de Storage con lazy import

    Returns:
        storage.Client: Cliente de GCS o None si falla
    """
    try:
        from google.cloud import storage

        return storage.Client()
    except Exception as e:
        logger.error(f"Error al crear cliente Storage: {e}")
        return None


def is_gcp_environment():
    """
    Detecta si estamos en entorno GCP

    Returns:
        bool: True si estamos en GCP
    """
    return (
        os.getenv("GAE_ENV", "").startswith("standard")
        or os.getenv("K_SERVICE")
        or bool(os.getenv("GOOGLE_CLOUD_PROJECT"))
    )


def upload_file(file, folder, filename=None):
    """
    Sube archivo a Cloud Storage o filesystem local

    Args:
        file: FileStorage object de Flask
        folder: Carpeta destino ('ordenes', 'manuales')
        filename: Nombre opcional (si None, usa file.filename)

    Returns:
        str: URL pública/local o None si falla
    """
    # Validar tamaño
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    if size > MAX_FILE_SIZE:
        logger.error(f"Archivo demasiado grande: {size} bytes (máx {MAX_FILE_SIZE})")
        return None

    # Detectar entorno
    if is_gcp_environment():
        # PRODUCCIÓN: Cloud Storage
        return _upload_to_gcs(file, folder, filename)
    else:
        # DESARROLLO: Sistema de archivos local
        return _upload_to_local(file, folder, filename)


def _upload_to_gcs(file, folder, filename):
    """
    Subida a Google Cloud Storage

    Args:
        file: FileStorage object
        folder: Carpeta destino
        filename: Nombre del archivo

    Returns:
        str: URL pública o None
    """
    try:
        client = get_storage_client()
        if not client:
            logger.error("No se pudo crear cliente de Storage")
            return None

        bucket = client.bucket(BUCKET_NAME)

        # Nombre seguro
        if not filename:
            filename = secure_filename(file.filename)

        blob_path = f"{folder}/{filename}"
        blob = bucket.blob(blob_path)

        # Subir
        blob.upload_from_file(file, content_type=file.content_type)

        logger.info(f"[OK] Archivo subido a GCS: {blob_path}")

        # Devolver path relativo (usaremos URLs firmadas para acceso)
        return f"gs://{BUCKET_NAME}/{blob_path}"

    except Exception as e:
        logger.error(f"Error subiendo a GCS: {e}")
        return None


def _upload_to_local(file, folder, filename):
    """
    Subida a filesystem local (desarrollo)

    Args:
        file: FileStorage object
        folder: Carpeta destino
        filename: Nombre del archivo

    Returns:
        str: Ruta local o None
    """
    try:
        # Directorio base
        base_dir = os.path.join("uploads", folder)
        os.makedirs(base_dir, exist_ok=True)

        # Nombre seguro
        if not filename:
            filename = secure_filename(file.filename)

        filepath = os.path.join(base_dir, filename)
        file.save(filepath)

        logger.info(f"[OK] Archivo guardado localmente: {filepath}")
        return f"/uploads/{folder}/{filename}"

    except Exception as e:
        logger.error(f"Error guardando localmente: {e}")
        return None


def delete_file(filepath, folder):
    """
    Elimina archivo de Storage

    Args:
        filepath: Ruta o URL del archivo
        folder: Carpeta ('ordenes', 'manuales')

    Returns:
        bool: True si se eliminó correctamente
    """
    if is_gcp_environment() or filepath.startswith("gs://"):
        return _delete_from_gcs(filepath, folder)
    else:
        return _delete_from_local(filepath, folder)


def _delete_from_gcs(filepath, folder):
    """
    Eliminar de Cloud Storage

    Args:
        filepath: URL de GCS (gs://bucket/path) o path relativo
        folder: Carpeta

    Returns:
        bool: True si se eliminó
    """
    try:
        client = get_storage_client()
        if not client:
            return False

        bucket = client.bucket(BUCKET_NAME)

        # Extraer path del blob
        if filepath.startswith("gs://"):
            # gs://bucket/folder/file.ext -> folder/file.ext
            blob_path = "/".join(filepath.split("/")[3:])
        else:
            # Asumir que es el nombre del archivo
            filename = os.path.basename(filepath)
            blob_path = f"{folder}/{filename}"

        blob = bucket.blob(blob_path)

        if blob.exists():
            blob.delete()
            logger.info(f"[OK] Archivo eliminado de GCS: {blob_path}")
            return True
        else:
            logger.warning(f"[WARN] Archivo no existe en GCS: {blob_path}")
            return False

    except Exception as e:
        logger.error(f"Error eliminando de GCS: {e}")
        return False


def _delete_from_local(filepath, folder):
    """
    Eliminar de filesystem local

    Args:
        filepath: Ruta local
        folder: Carpeta

    Returns:
        bool: True si se eliminó
    """
    try:
        # filepath puede ser relativo o absoluto
        if filepath.startswith("/uploads/"):
            filepath = filepath[1:]  # Quitar '/' inicial

        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"[OK] Archivo eliminado localmente: {filepath}")
            return True
        else:
            logger.warning(f"[WARN] Archivo no existe localmente: {filepath}")
            return False

    except Exception as e:
        logger.error(f"Error eliminando localmente: {e}")
        return False


def get_signed_url(filepath, folder, expiration=3600):
    """
    Genera URL firmada para descarga segura (solo GCP)

    Args:
        filepath: Ruta del archivo (gs:// o path relativo)
        folder: Carpeta
        expiration: Segundos de validez (default 1 hora)

    Returns:
        str: URL firmada o URL normal si es local
    """
    # Si es local, devolver URL normal
    if not is_gcp_environment() and not filepath.startswith("gs://"):
        return filepath

    try:
        client = get_storage_client()
        if not client:
            logger.warning("No se pudo crear cliente Storage, devolviendo URL original")
            return filepath

        bucket = client.bucket(BUCKET_NAME)

        # Extraer path del blob
        if filepath.startswith("gs://"):
            blob_path = "/".join(filepath.split("/")[3:])
        else:
            filename = os.path.basename(filepath)
            blob_path = f"{folder}/{filename}"

        blob = bucket.blob(blob_path)

        # Verificar que existe
        if not blob.exists():
            logger.warning(f"[WARN] Blob no existe: {blob_path}")
            return filepath

        # URL firmada válida por el tiempo especificado
        url = blob.generate_signed_url(
            version="v4", expiration=timedelta(seconds=expiration), method="GET"
        )

        logger.debug(f"URL firmada generada para {blob_path}")
        return url

    except Exception as e:
        logger.error(f"Error generando URL firmada: {e}")
        return filepath


def list_files(folder, prefix=""):
    """
    Lista archivos en una carpeta

    Args:
        folder: Carpeta ('ordenes', 'manuales')
        prefix: Filtro opcional de prefijo

    Returns:
        list: Lista de nombres de archivo
    """
    if is_gcp_environment():
        return _list_from_gcs(folder, prefix)
    else:
        return _list_from_local(folder, prefix)


def _list_from_gcs(folder, prefix):
    """
    Listar archivos de Cloud Storage

    Args:
        folder: Carpeta
        prefix: Prefijo de filtro

    Returns:
        list: Nombres de archivos
    """
    try:
        client = get_storage_client()
        if not client:
            return []

        bucket = client.bucket(BUCKET_NAME)
        blob_prefix = f"{folder}/{prefix}" if prefix else f"{folder}/"

        blobs = bucket.list_blobs(prefix=blob_prefix)
        files = []

        for blob in blobs:
            # Extraer solo el nombre del archivo
            filename = blob.name.split("/")[-1]
            if filename:  # Evitar carpetas vacías
                files.append(filename)

        return files

    except Exception as e:
        logger.error(f"Error listando de GCS: {e}")
        return []


def _list_from_local(folder, prefix):
    """
    Listar archivos locales

    Args:
        folder: Carpeta
        prefix: Prefijo de filtro

    Returns:
        list: Nombres de archivos
    """
    try:
        base_dir = os.path.join("uploads", folder)
        if not os.path.exists(base_dir):
            return []

        files = os.listdir(base_dir)

        if prefix:
            files = [f for f in files if f.startswith(prefix)]

        return files

    except Exception as e:
        logger.error(f"Error listando localmente: {e}")
        return []


def file_exists(filepath, folder):
    """
    Verifica si un archivo existe

    Args:
        filepath: Ruta o URL del archivo
        folder: Carpeta

    Returns:
        bool: True si existe
    """
    if is_gcp_environment() or filepath.startswith("gs://"):
        return _file_exists_gcs(filepath, folder)
    else:
        return _file_exists_local(filepath, folder)


def _file_exists_gcs(filepath, folder):
    """Verificar existencia en GCS"""
    try:
        client = get_storage_client()
        if not client:
            return False

        bucket = client.bucket(BUCKET_NAME)

        if filepath.startswith("gs://"):
            blob_path = "/".join(filepath.split("/")[3:])
        else:
            filename = os.path.basename(filepath)
            blob_path = f"{folder}/{filename}"

        blob = bucket.blob(blob_path)
        return blob.exists()

    except Exception as e:
        logger.error(f"Error verificando existencia en GCS: {e}")
        return False


def _file_exists_local(filepath, folder):
    """Verificar existencia local"""
    try:
        if filepath.startswith("/uploads/"):
            filepath = filepath[1:]

        return os.path.exists(filepath)

    except Exception as e:
        logger.error(f"Error verificando existencia local: {e}")
        return False
