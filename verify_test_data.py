#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.extensions import db
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.models.activo import Activo
from app.models.solicitud_servicio import SolicitudServicio

def verificar_datos_prueba():
    """Verificar que los datos de prueba se crearon correctamente"""
    app = create_app()
    
    with app.app_context():
        print("=== VERIFICACIÓN DE DATOS DE PRUEBA ===\n")
        
        # Verificar usuarios
        usuarios = Usuario.query.all()
        print(f"👤 Usuarios en la base de datos: {len(usuarios)}")
        for usuario in usuarios:
            print(f"   - {usuario.username} ({usuario.rol}) - Email: {usuario.email}")
        
        # Verificar categorías
        categorias = Categoria.query.all()
        print(f"\n📂 Categorías en la base de datos: {len(categorias)}")
        for categoria in categorias:
            print(f"   - {categoria.nombre}: {categoria.descripcion}")
        
        # Verificar activos
        activos = Activo.query.all()
        print(f"\n🏭 Activos en la base de datos: {len(activos)}")
        for activo in activos:
            print(f"   - {activo.codigo}: {activo.nombre} ({activo.tipo}) - Estado: {activo.estado}")
        
        # Verificar solicitudes de servicio
        solicitudes = SolicitudServicio.query.all()
        print(f"\n📋 Solicitudes de servicio en la base de datos: {len(solicitudes)}")
        for solicitud in solicitudes:
            print(f"   - {solicitud.numero_solicitud}: {solicitud.titulo}")
            print(f"     Estado: {solicitud.estado} | Prioridad: {solicitud.prioridad}")
            print(f"     Solicitante: {solicitud.nombre_solicitante}")
            if solicitud.activo_id:
                activo = Activo.query.get(solicitud.activo_id)
                print(f"     Activo relacionado: {activo.nombre if activo else 'No encontrado'}")
            print()
        
        print("=== RESUMEN ===")
        print(f"Total de registros: {len(usuarios) + len(categorias) + len(activos) + len(solicitudes)}")
        print("\n✅ Verificación completada. Los datos están listos para probar la funcionalidad de eliminación.")

if __name__ == "__main__":
    try:
        verificar_datos_prueba()
    except Exception as e:
        print(f"❌ Error verificando datos de prueba: {e}")
        import traceback
        traceback.print_exc()