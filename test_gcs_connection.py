#!/usr/bin/env python3
"""
Script para probar la conexión a Google Cloud Storage
"""

import os
import sys

def test_gcs_connection():
    """Prueba la conexión a GCS"""
    try:
        from google.cloud import storage
        
        print("🔍 Probando conexión a Google Cloud Storage...")
        
        # Mostrar información del entorno
        print(f"📊 GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'No configurado')}")
        print(f"📊 GOOGLE_CLOUD_PROJECT: {os.getenv('GOOGLE_CLOUD_PROJECT', 'No configurado')}")
        
        # Crear cliente
        client = storage.Client()
        print(f"✅ Cliente creado exitosamente")
        print(f"📊 Proyecto del cliente: {client.project}")
        
        # Listar buckets del proyecto
        print("📊 Buckets disponibles:")
        try:
            buckets = list(client.list_buckets())
            for bucket in buckets:
                print(f"   - {bucket.name}")
        except Exception as e:
            print(f"❌ Error listando buckets: {e}")
        
        # Probar acceso al bucket específico
        bucket_name = "gmao-uploads"
        bucket = client.bucket(bucket_name)
        
        print(f"🔍 Verificando bucket: {bucket_name}")
        
        if bucket.exists():
            print(f"✅ Bucket existe: {bucket_name}")
            
            # Listar algunos objetos
            blobs = list(bucket.list_blobs(max_results=5))
            print(f"📊 Objetos en bucket: {len(blobs)}")
            
            for blob in blobs:
                print(f"   - {blob.name}")
                
            return True
        else:
            print(f"❌ Bucket no existe: {bucket_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gcs_connection()
    sys.exit(0 if success else 1)