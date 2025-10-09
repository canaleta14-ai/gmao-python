#!/usr/bin/env python3
"""
Script para migrar archivos de solicitudes desde filesystem local a Google Cloud Storage
EJECUTAR UNA SOLA VEZ antes del deploy a producción
"""

import os
import sys
from pathlib import Path

# Añadir path del proyecto
sys.path.insert(0, str(Path(__file__).parent))

from app.factory import create_app
from app.models.archivo_adjunto import ArchivoAdjunto
from app.extensions import db
from app.utils.storage import get_storage_client, BUCKET_NAME
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_solicitudes_files():
    """Migra archivos de solicitudes desde filesystem local a Google Cloud Storage"""
    
    app = create_app()
    
    with app.app_context():
        print("🔄 Migrando archivos de solicitudes a Google Cloud Storage...")
        print(f"📦 Bucket destino: {BUCKET_NAME}")
        print("-" * 60)
        
        try:
            # Verificar conexión a GCS
            client = get_storage_client()
            if not client:
                print("❌ Error: No se pudo conectar a Google Cloud Storage")
                print("   Verifica que:")
                print("   1. google-cloud-storage esté instalado")
                print("   2. Las credenciales de GCP estén configuradas")
                print("   3. El proyecto tenga permisos de Storage")
                return False
            
            bucket = client.bucket(BUCKET_NAME)
            
            # Verificar que el bucket existe
            if not bucket.exists():
                print(f"❌ Error: El bucket '{BUCKET_NAME}' no existe")
                print(f"   Crear con: gcloud storage buckets create gs://{BUCKET_NAME}")
                return False
            
            print(f"✅ Conectado a bucket: {BUCKET_NAME}")
            
            # Obtener todos los archivos adjuntos de solicitudes
            archivos = ArchivoAdjunto.query.filter(
                ArchivoAdjunto.solicitud_servicio_id.isnot(None)
            ).all()
            
            if not archivos:
                print("ℹ️  No se encontraron archivos de solicitudes para migrar")
                return True
            
            print(f"📊 Encontrados {len(archivos)} archivos de solicitudes")
            print("-" * 60)
            
            migrated = 0
            errors = 0
            skipped = 0
            
            for archivo in archivos:
                print(f"📄 Procesando: {archivo.nombre_original} (ID: {archivo.id})")
                
                # Verificar si ya está en GCS
                if archivo.ruta_archivo.startswith("gs://"):
                    print(f"   ⏭️  Ya está en GCS: {archivo.ruta_archivo}")
                    skipped += 1
                    continue
                
                # Verificar que el archivo local existe
                local_path = Path(archivo.ruta_archivo)
                if not local_path.exists():
                    print(f"   ⚠️  Archivo local no encontrado: {local_path}")
                    errors += 1
                    continue
                
                try:
                    # Construir path en GCS
                    solicitud_id = archivo.solicitud_servicio_id
                    gcs_path = f"solicitudes/{solicitud_id}/{archivo.nombre_archivo}"
                    blob = bucket.blob(gcs_path)
                    
                    # Subir archivo a GCS
                    print(f"   ⬆️  Subiendo a: gs://{BUCKET_NAME}/{gcs_path}")
                    blob.upload_from_filename(str(local_path))
                    
                    # Actualizar ruta en base de datos
                    nueva_ruta = f"gs://{BUCKET_NAME}/{gcs_path}"
                    archivo.ruta_archivo = nueva_ruta
                    
                    print(f"   ✅ Migrado exitosamente")
                    migrated += 1
                    
                except Exception as e:
                    print(f"   ❌ Error migrando: {e}")
                    errors += 1
                    continue
            
            # Guardar cambios en la base de datos
            if migrated > 0:
                try:
                    db.session.commit()
                    print("-" * 60)
                    print(f"💾 Cambios guardados en la base de datos")
                except Exception as e:
                    print(f"❌ Error guardando cambios: {e}")
                    db.session.rollback()
                    return False
            
            # Resumen final
            print("-" * 60)
            print("📊 RESUMEN DE MIGRACIÓN:")
            print(f"   ✅ Migrados exitosamente: {migrated}")
            print(f"   ⏭️  Ya estaban en GCS: {skipped}")
            print(f"   ❌ Errores: {errors}")
            print(f"   📁 Total procesados: {len(archivos)}")
            
            if errors == 0:
                print("\n🎉 ¡Migración completada exitosamente!")
                print("\n📋 PRÓXIMOS PASOS:")
                print("   1. Verificar que los archivos están en GCS")
                print("   2. Hacer deploy de la aplicación")
                print("   3. Probar descarga de archivos en producción")
                print("   4. Opcional: Limpiar archivos locales antiguos")
                return True
            else:
                print(f"\n⚠️  Migración completada con {errors} errores")
                print("   Revisar los errores antes de hacer deploy")
                return False
                
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            return False

def verify_migration():
    """Verifica que la migración se completó correctamente"""
    
    app = create_app()
    
    with app.app_context():
        print("\n🔍 Verificando migración...")
        
        # Contar archivos por tipo de almacenamiento
        total_archivos = ArchivoAdjunto.query.filter(
            ArchivoAdjunto.solicitud_servicio_id.isnot(None)
        ).count()
        
        archivos_gcs = ArchivoAdjunto.query.filter(
            ArchivoAdjunto.solicitud_servicio_id.isnot(None),
            ArchivoAdjunto.ruta_archivo.like('gs://%')
        ).count()
        
        archivos_local = total_archivos - archivos_gcs
        
        print(f"📊 ESTADO ACTUAL:")
        print(f"   📁 Total archivos de solicitudes: {total_archivos}")
        print(f"   ☁️  En Google Cloud Storage: {archivos_gcs}")
        print(f"   💻 En filesystem local: {archivos_local}")
        
        if archivos_local == 0:
            print("✅ Todos los archivos están en Google Cloud Storage")
        else:
            print(f"⚠️  Quedan {archivos_local} archivos en filesystem local")

if __name__ == "__main__":
    print("🚀 MIGRACIÓN DE ARCHIVOS DE SOLICITUDES A GOOGLE CLOUD STORAGE")
    print("=" * 70)
    
    # Verificar estado actual
    verify_migration()
    
    # Confirmar migración
    print("\n" + "=" * 70)
    respuesta = input("¿Continuar con la migración? (s/N): ").lower().strip()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        success = migrate_solicitudes_files()
        
        if success:
            print("\n" + "=" * 70)
            verify_migration()
        
        sys.exit(0 if success else 1)
    else:
        print("❌ Migración cancelada por el usuario")
        sys.exit(0)