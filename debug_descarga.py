#!/usr/bin/env python3

import os
import sys
import traceback

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.models.archivo_adjunto import ArchivoAdjunto
from app.utils.storage import file_exists, is_gcp_environment, _file_exists_gcs, get_storage_client, BUCKET_NAME

def debug_file_exists(filepath, folder=""):
    """Versión de debug de file_exists que muestra todo el flujo interno"""
    print(f"\n🔍 DEBUG file_exists:")
    print(f"   filepath: '{filepath}'")
    print(f"   folder: '{folder}'")
    
    # Verificar si es un path de GCS
    is_gcs_path = filepath.startswith("gs://")
    print(f"   filepath.startswith('gs://'): {is_gcs_path}")
    
    # Verificar si estamos en entorno GCP
    is_gcp = is_gcp_environment()
    print(f"   is_gcp_environment(): {is_gcp}")
    
    # Determinar qué camino tomar
    if is_gcs_path:
        print(f"   Tomando camino GCS (por path gs://)")
        try:
            # Extraer bucket y path
            path_parts = filepath.replace("gs://", "").split("/", 1)
            bucket_name = path_parts[0]
            blob_path = path_parts[1] if len(path_parts) > 1 else ""
            print(f"   bucket_name: '{bucket_name}'")
            print(f"   blob_path: '{blob_path}'")
            
            # Verificar en GCS
            result = _file_exists_gcs(filepath=filepath)
            print(f"   _file_exists_gcs resultado: {result}")
            return result
        except Exception as e:
            print(f"   ❌ Excepción en camino GCS: {e}")
            traceback.print_exc()
            return False
    elif is_gcp:
        print(f"   Tomando camino GCS (por is_gcp_environment)")
        try:
            # Construir path completo
            if folder:
                if not filepath.startswith("/"):
                    full_path = f"{folder}/{filepath}"
                else:
                    full_path = f"{folder}{filepath}"
            else:
                full_path = filepath
                
            print(f"   full_path construido: '{full_path}'")
            
            # Verificar en GCS
            result = _file_exists_gcs(filepath=full_path, folder="")
            print(f"   _file_exists_gcs resultado: {result}")
            return result
        except Exception as e:
            print(f"   ❌ Excepción en camino GCS (is_gcp): {e}")
            traceback.print_exc()
            return False
    else:
        print(f"   Tomando camino local")
        try:
            # Construir path local
            if folder:
                if not filepath.startswith("/"):
                    full_path = os.path.join(folder, filepath)
                else:
                    full_path = folder + filepath
            else:
                full_path = filepath
                
            print(f"   full_path local: '{full_path}'")
            
            # Verificar existencia local
            exists = os.path.exists(full_path)
            print(f"   os.path.exists resultado: {exists}")
            return exists
        except Exception as e:
            print(f"   ❌ Excepción en camino local: {e}")
            traceback.print_exc()
            return False

def debug_file_exists_gcs(filepath="", folder=""):
    """Versión de debug de _file_exists_gcs"""
    print(f"\n🔍 DEBUG _file_exists_gcs:")
    print(f"   filepath: '{filepath}'")
    print(f"   folder: '{folder}'")
    
    try:
        # Obtener cliente de storage
        client = get_storage_client()
        print(f"   client: {client}")
        
        if not client:
            print("   ❌ No se pudo obtener cliente de storage")
            return False
            
        # Obtener bucket
        bucket = client.bucket(BUCKET_NAME)
        print(f"   bucket: {bucket}")
        
        # Determinar blob_path
        if filepath.startswith("gs://"):
            # Extraer path del blob
            path_parts = filepath.replace("gs://", "").split("/", 1)
            if len(path_parts) > 1:
                blob_path = path_parts[1]
            else:
                blob_path = ""
            print(f"   blob_path (desde gs://): '{blob_path}'")
        else:
            # Construir path del blob
            if folder:
                if not filepath.startswith("/"):
                    blob_path = f"{folder}/{filepath}"
                else:
                    blob_path = f"{folder}{filepath}"
            else:
                blob_path = filepath
            print(f"   blob_path (construido): '{blob_path}'")
            
        # Verificar existencia del blob
        blob = bucket.blob(blob_path)
        print(f"   blob: {blob}")
        
        exists = blob.exists()
        print(f"   blob.exists(): {exists}")
        return exists
        
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        traceback.print_exc()
        return False

def main():
    app = create_app()
    
    with app.app_context():
        print("🔍 Debuggeando file_exists en contexto Flask...")
        
        # Obtener el archivo
        archivo = ArchivoAdjunto.query.get(1)
        if not archivo:
            print("❌ No se encontró el archivo con ID 1")
            return
            
        print(f"📁 Archivo encontrado:")
        print(f"   ID: {archivo.id}")
        print(f"   Nombre: {archivo.nombre_original}")
        print(f"   Ruta: {archivo.ruta_archivo}")
        
        # Probar file_exists con nuestra función de debug
        print("\n🔍 Probando debug_file_exists...")
        exists = debug_file_exists(archivo.ruta_archivo, "")
        print(f"   Resultado final: {exists}")
        
        # Probar _file_exists_gcs directamente
        print("\n🔍 Probando debug_file_exists_gcs directamente...")
        exists_gcs = debug_file_exists_gcs(archivo.ruta_archivo, "")
        print(f"   Resultado final: {exists_gcs}")
        
        # Probar file_exists original para comparar
        print("\n🔍 Probando file_exists original...")
        exists_orig = file_exists(archivo.ruta_archivo, "")
        print(f"   Resultado: {exists_orig}")

if __name__ == "__main__":
    main()