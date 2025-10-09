#!/usr/bin/env python3
"""
Script de migración para mover archivos adjuntos de órdenes 
desde filesystem local a Google Cloud Storage

Uso:
    python migrate_ordenes_to_gcs.py [--dry-run] [--verify-only]
    
Opciones:
    --dry-run: Solo mostrar qué archivos se migrarían sin hacer cambios
    --verify-only: Solo verificar el estado actual de la migración
"""

import os
import sys
import argparse
from datetime import datetime

# Agregar el directorio raíz al path para importar módulos de la app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.models import ArchivoAdjunto
from app.extensions import db
from app.utils.storage import get_storage_client, is_gcp_environment, BUCKET_NAME


def conectar_gcs():
    """Conectar a Google Cloud Storage"""
    try:
        client = get_storage_client()
        bucket = client.bucket(BUCKET_NAME)
        
        # Verificar que el bucket existe
        if not bucket.exists():
            print(f"❌ Error: El bucket '{BUCKET_NAME}' no existe")
            return None, None
            
        print(f"✅ Conectado a GCS bucket: {BUCKET_NAME}")
        return client, bucket
    except Exception as e:
        print(f"❌ Error conectando a GCS: {e}")
        return None, None


def verificar_migracion():
    """Verificar el estado actual de la migración"""
    print("🔍 Verificando estado de archivos de órdenes...")
    
    archivos = ArchivoAdjunto.query.filter(
        ArchivoAdjunto.orden_trabajo_id.isnot(None),
        ArchivoAdjunto.tipo_archivo != 'enlace'
    ).all()
    
    total = len(archivos)
    en_gcs = 0
    en_local = 0
    perdidos = 0
    
    print(f"\n📊 Encontrados {total} archivos de órdenes:")
    
    for archivo in archivos:
        print(f"\nID: {archivo.id}")
        print(f"  Nombre: {archivo.nombre_original}")
        print(f"  Orden ID: {archivo.orden_trabajo_id}")
        print(f"  Ruta: {archivo.ruta_archivo}")
        
        if archivo.ruta_archivo.startswith('gs://'):
            print(f"  Estado: ✅ En Google Cloud Storage")
            en_gcs += 1
        else:
            # Verificar si existe localmente
            ruta_local = os.path.join('static', archivo.ruta_archivo)
            if os.path.exists(ruta_local):
                print(f"  Estado: 📁 En filesystem local")
                en_local += 1
            else:
                print(f"  Estado: ❌ PERDIDO - No existe en local ni en GCS")
                perdidos += 1
        
        print("-" * 50)
    
    print(f"\n📈 Resumen:")
    print(f"  Total de archivos: {total}")
    print(f"  En Google Cloud Storage: {en_gcs}")
    print(f"  En filesystem local: {en_local}")
    print(f"  Perdidos: {perdidos}")
    
    return {
        'total': total,
        'en_gcs': en_gcs,
        'en_local': en_local,
        'perdidos': perdidos
    }


def migrar_archivos(dry_run=False):
    """Migrar archivos de órdenes a Google Cloud Storage"""
    
    if not is_gcp_environment() and not dry_run:
        print("⚠️  Advertencia: No estás en entorno GCP. Los archivos se migrarán pero no se podrán acceder desde producción.")
        respuesta = input("¿Continuar? (y/N): ")
        if respuesta.lower() != 'y':
            return
    
    # Conectar a GCS
    client, bucket = conectar_gcs()
    if not client:
        return
    
    # Obtener archivos de órdenes que están en filesystem local
    archivos_locales = ArchivoAdjunto.query.filter(
        ArchivoAdjunto.orden_trabajo_id.isnot(None),
        ArchivoAdjunto.tipo_archivo != 'enlace',
        ~ArchivoAdjunto.ruta_archivo.like('gs://%')
    ).all()
    
    total = len(archivos_locales)
    print(f"\n🚀 Iniciando migración de {total} archivos de órdenes...")
    
    if dry_run:
        print("🔍 MODO DRY-RUN - No se harán cambios reales")
    
    migrados = 0
    errores = 0
    
    for i, archivo in enumerate(archivos_locales, 1):
        print(f"\n[{i}/{total}] Procesando: {archivo.nombre_original}")
        
        # Verificar que el archivo existe localmente
        ruta_local = os.path.join('static', archivo.ruta_archivo)
        if not os.path.exists(ruta_local):
            print(f"  ❌ Archivo no encontrado: {ruta_local}")
            errores += 1
            continue
        
        # Generar ruta en GCS
        folder = "ordenes"
        filename = archivo.nombre_archivo
        blob_name = f"{folder}/{filename}"
        
        print(f"  📤 Subiendo a: gs://{BUCKET_NAME}/{blob_name}")
        
        if not dry_run:
            try:
                # Subir archivo a GCS
                blob = bucket.blob(blob_name)
                blob.upload_from_filename(ruta_local)
                
                # Actualizar ruta en base de datos
                archivo.ruta_archivo = f"gs://{BUCKET_NAME}/{blob_name}"
                db.session.add(archivo)
                
                print(f"  ✅ Migrado exitosamente")
                migrados += 1
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                errores += 1
        else:
            print(f"  🔍 [DRY-RUN] Se migraría a: gs://{BUCKET_NAME}/{blob_name}")
            migrados += 1
    
    if not dry_run and migrados > 0:
        try:
            db.session.commit()
            print(f"\n✅ Base de datos actualizada")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error actualizando base de datos: {e}")
            return
    
    print(f"\n📊 Resumen de migración:")
    print(f"  Archivos procesados: {total}")
    print(f"  Migrados exitosamente: {migrados}")
    print(f"  Errores: {errores}")
    
    if not dry_run and migrados > 0:
        print(f"\n🎉 Migración completada!")
        print(f"💡 Tip: Puedes ejecutar con --verify-only para verificar el resultado")


def main():
    parser = argparse.ArgumentParser(description='Migrar archivos de órdenes a Google Cloud Storage')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Solo mostrar qué archivos se migrarían sin hacer cambios')
    parser.add_argument('--verify-only', action='store_true',
                       help='Solo verificar el estado actual de la migración')
    
    args = parser.parse_args()
    
    # Crear contexto de aplicación
    app = create_app()
    
    with app.app_context():
        print("🔧 Script de Migración de Archivos de Órdenes a Google Cloud Storage")
        print("=" * 70)
        
        if args.verify_only:
            verificar_migracion()
        else:
            # Verificar estado actual
            estado = verificar_migracion()
            
            if estado['en_local'] == 0:
                print("\n✅ No hay archivos locales para migrar")
                return
            
            print(f"\n🚀 Se migrarán {estado['en_local']} archivos a Google Cloud Storage")
            
            if not args.dry_run:
                respuesta = input("\n¿Proceder con la migración? (y/N): ")
                if respuesta.lower() != 'y':
                    print("Migración cancelada")
                    return
            
            migrar_archivos(dry_run=args.dry_run)


if __name__ == "__main__":
    main()