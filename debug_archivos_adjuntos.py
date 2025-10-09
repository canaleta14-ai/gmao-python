#!/usr/bin/env python3
"""
Script para verificar archivos adjuntos en la base de datos
"""

import os
from app.factory import create_app
from app.models.archivo_adjunto import ArchivoAdjunto
from app.extensions import db

def verificar_archivos():
    """Verificar archivos adjuntos en la base de datos"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 Verificando archivos adjuntos en la base de datos...\n")
        
        try:
            # Obtener todos los archivos adjuntos
            archivos = ArchivoAdjunto.query.all()
            
            if not archivos:
                print("❌ No se encontraron archivos adjuntos en la base de datos")
                return
            
            print(f"📊 Encontrados {len(archivos)} archivos adjuntos:\n")
            
            for archivo in archivos:
                print(f"ID: {archivo.id}")
                print(f"  Nombre original: {archivo.nombre_original}")
                print(f"  Nombre archivo: {archivo.nombre_archivo}")
                print(f"  Tipo: {archivo.tipo_archivo}")
                print(f"  Ruta: {archivo.ruta_archivo}")
                print(f"  Solicitud ID: {archivo.solicitud_servicio_id}")
                print(f"  Orden ID: {archivo.orden_trabajo_id}")
                
                # Verificar si el archivo existe físicamente
                if archivo.ruta_archivo:
                    existe = os.path.exists(archivo.ruta_archivo)
                    print(f"  Archivo existe: {'✅ SÍ' if existe else '❌ NO'}")
                else:
                    print(f"  Archivo existe: ❌ Sin ruta")
                
                print("-" * 50)
                
        except Exception as e:
            print(f"❌ Error al verificar archivos: {e}")

if __name__ == "__main__":
    verificar_archivos()