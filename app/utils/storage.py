"""
Utilidades para almacenamiento local de archivos
Maneja persistencia de archivos en filesystem local
"""

import os
import logging
from werkzeug.utils import secure_filename
import shutil

logger = logging.getLogger(__name__)

# Configuración
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Crear directorio de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def is_gcp_environment():
    """
    Detecta si estamos en entorno GCP (siempre False en desarrollo local)

    Returns:
        bool: False (desarrollo local)
    """
    return False


def upload_file(file_obj, subfolder="", filename=None):
    """
    Sube archivo al filesystem local

    Args:
        file_obj: Objeto de archivo (FileStorage)
        subfolder: Subcarpeta opcional
        filename: Nombre del archivo (opcional, si no se proporciona usa file_obj.filename)

    Returns:
        str: Ruta del archivo guardado o None si falla
    """
    try:
        if not file_obj:
            logger.error("No se proporcionó archivo")
            return None

        # Usar filename proporcionado o el del objeto
        if not filename:
            filename = file_obj.filename if hasattr(file_obj, "filename") else "file"

        # Sanitizar nombre del archivo
        secure_name = secure_filename(filename)
        if not secure_name:
            logger.error(f"Nombre de archivo inválido: {filename}")
            return None

        # Crear directorio si incluye subfolder
        upload_path = UPLOAD_FOLDER
        if subfolder:
            upload_path = os.path.join(UPLOAD_FOLDER, subfolder)
            os.makedirs(upload_path, exist_ok=True)

        # Ruta completa del archivo
        file_path = os.path.join(upload_path, secure_name)

        # Guardar archivo
        file_obj.save(file_path)

        # Retornar ruta relativa
        relative_path = os.path.relpath(file_path, os.getcwd())
        logger.info(f"Archivo guardado: {relative_path}")
        return relative_path

    except Exception as e:
        logger.error(f"Error al subir archivo {filename}: {e}")
        return None


def file_exists(filepath):
    """
    Verificar si archivo existe en filesystem local

    Args:
        filepath: Ruta del archivo

    Returns:
        bool: True si existe
    """
    if not filepath:
        return False

    # Convertir a ruta absoluta si es relativa
    if not os.path.isabs(filepath):
        filepath = os.path.join(os.getcwd(), filepath)

    return os.path.exists(filepath)


def delete_file(filepath, subfolder=""):
    """
    Eliminar archivo del filesystem local

    Args:
        filepath: Ruta del archivo o nombre del archivo
        subfolder: Subcarpeta opcional (para compatibilidad con GCS)

    Returns:
        bool: True si se eliminó correctamente
    """
    try:
        if not filepath:
            return False

        # Si filepath ya es una ruta completa, usarla directamente
        if os.path.isabs(filepath) or filepath.startswith("uploads"):
            full_path = (
                filepath
                if os.path.isabs(filepath)
                else os.path.join(os.getcwd(), filepath)
            )
        else:
            # Construir ruta con subfolder
            if subfolder:
                full_path = os.path.join(UPLOAD_FOLDER, subfolder, filepath)
            else:
                full_path = os.path.join(UPLOAD_FOLDER, filepath)

        if os.path.exists(full_path):
            os.remove(full_path)
            logger.info(f"Archivo eliminado: {full_path}")
            return True
        else:
            logger.warning(f"Archivo no encontrado: {full_path}")
            return False

    except Exception as e:
        logger.error(f"Error al eliminar archivo {filepath}: {e}")
        return False


def get_signed_url(filepath, subfolder="", expiration=60):
    """
    Genera URL local para descarga (desarrollo local - no URLs firmadas)

    Args:
        filepath: Ruta del archivo
        subfolder: Subcarpeta (para compatibilidad con GCS)
        expiration: Tiempo de expiración en segundos (no usado en desarrollo local)

    Returns:
        str: Ruta local del archivo o None si no existe
    """
    # Si filepath ya contiene la ruta completa, verificar existencia
    if file_exists(filepath):
        if not os.path.isabs(filepath):
            return filepath
        else:
            return os.path.relpath(filepath, os.getcwd())

    # Si no existe, intentar construir ruta con subfolder
    if subfolder:
        full_path = os.path.join(UPLOAD_FOLDER, subfolder, filepath)
        if file_exists(full_path):
            return os.path.relpath(full_path, os.getcwd())

    return None


def list_files(prefix=""):
    """
    Listar archivos del directorio uploads

    Args:
        prefix: Prefijo de búsqueda (subfolder)

    Returns:
        list: Lista de archivos encontrados
    """
    try:
        search_path = UPLOAD_FOLDER
        if prefix:
            search_path = os.path.join(UPLOAD_FOLDER, prefix)

        if not os.path.exists(search_path):
            return []

        files = []
        for root, dirs, filenames in os.walk(search_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, os.getcwd())
                files.append(relative_path)

        return files

    except Exception as e:
        logger.error(f"Error al listar archivos: {e}")
        return []


def get_file_size(filepath):
    """
    Obtener tamaño del archivo en bytes

    Args:
        filepath: Ruta del archivo

    Returns:
        int: Tamaño en bytes o None si no existe
    """
    try:
        if not os.path.isabs(filepath):
            filepath = os.path.join(os.getcwd(), filepath)

        if os.path.exists(filepath):
            return os.path.getsize(filepath)
        else:
            return None

    except Exception as e:
        logger.error(f"Error al obtener tamaño de {filepath}: {e}")
        return None


def copy_file(source_path, dest_path):
    """
    Copiar archivo de una ubicación a otra

    Args:
        source_path: Ruta origen
        dest_path: Ruta destino

    Returns:
        bool: True si se copió correctamente
    """
    try:
        # Crear directorio destino si no existe
        dest_dir = os.path.dirname(dest_path)
        if dest_dir:
            os.makedirs(dest_dir, exist_ok=True)

        shutil.copy2(source_path, dest_path)
        logger.info(f"Archivo copiado: {source_path} -> {dest_path}")
        return True

    except Exception as e:
        logger.error(f"Error al copiar archivo: {e}")
        return False
