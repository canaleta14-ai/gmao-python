#!/usr/bin/env python3

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.models.archivo_adjunto import ArchivoAdjunto
from app.models.solicitud_servicio import SolicitudServicio

def main():
    app = create_app()
    
    with app.app_context():
        print("🔍 Verificando archivos adjuntos...")
        
        # Verificar solicitudes
        solicitudes = SolicitudServicio.query.all()
        print(f"📋 Total solicitudes: {len(solicitudes)}")
        
        for solicitud in solicitudes:
            print(f"   Solicitud ID: {solicitud.id} - {solicitud.descripcion[:50]}...")
        
        # Verificar archivos adjuntos
        archivos = ArchivoAdjunto.query.all()
        print(f"📁 Total archivos adjuntos: {len(archivos)}")
        
        for archivo in archivos:
            print(f"   Archivo ID: {archivo.id}")
            print(f"   Nombre: {archivo.nombre_original}")
            print(f"   Ruta: {archivo.ruta_archivo}")
            print(f"   Solicitud ID: {archivo.solicitud_servicio_id}")
            print(f"   Orden ID: {archivo.orden_trabajo_id}")
            print("   ---")

if __name__ == "__main__":
    main()