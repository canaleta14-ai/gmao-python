#!/usr/bin/env python3
"""
Script para crear datos de prueba
"""

from flask import Flask
from app.factory import create_app
from app.extensions import db
from app.models.solicitud_servicio import SolicitudServicio
from app.models.activo import Activo
from app.models.categoria import Categoria
from app.models.usuario import Usuario
from datetime import datetime

def crear_datos_prueba():
    """Crea datos de prueba para testing"""
    print("🔧 Creando datos de prueba...")
    
    try:
        # Obtener el usuario admin
        admin_user = Usuario.query.filter_by(rol='Administrador').first()
        if not admin_user:
            print("❌ No se encontró usuario administrador")
            return False
        
        # Crear categoría de prueba
        categoria = Categoria(
            nombre='Equipos de Prueba',
            descripcion='Categoría para equipos de testing'
        )
        db.session.add(categoria)
        db.session.flush()  # Para obtener el ID
        
        # Crear activo de prueba
        activo = Activo(
            codigo='000-TEST-00001',
            departamento='000',
            nombre='Equipo de Prueba 1',
            descripcion='Equipo para testing de eliminación',
            tipo='Equipo de Laboratorio',
            ubicacion='Laboratorio de Pruebas',
            estado='Operativo'
        )
        db.session.add(activo)
        db.session.flush()  # Para obtener el ID
        
        # Crear solicitudes de servicio de prueba
        solicitudes = [
            {
                'numero_solicitud': 'SOL-TEST-001',
                'titulo': 'Solicitud de Prueba 1',
                'descripcion': 'Primera solicitud para testing de eliminación',
                'prioridad': 'normal',
                'estado': 'pendiente',
                'tipo_servicio': 'mantenimiento'
            },
            {
                'numero_solicitud': 'SOL-TEST-002',
                'titulo': 'Solicitud de Prueba 2',
                'descripcion': 'Segunda solicitud para testing de eliminación',
                'prioridad': 'alta',
                'estado': 'en_progreso',
                'tipo_servicio': 'reparacion'
            },
            {
                'numero_solicitud': 'SOL-TEST-003',
                'titulo': 'Solicitud de Prueba 3',
                'descripcion': 'Tercera solicitud para testing de eliminación',
                'prioridad': 'baja',
                'estado': 'pendiente',
                'tipo_servicio': 'instalacion'
            }
        ]
        
        for sol_data in solicitudes:
            solicitud = SolicitudServicio(
                numero_solicitud=sol_data['numero_solicitud'],
                titulo=sol_data['titulo'],
                descripcion=sol_data['descripcion'],
                prioridad=sol_data['prioridad'],
                estado=sol_data['estado'],
                tipo_servicio=sol_data['tipo_servicio'],
                nombre_solicitante=admin_user.nombre,
                email_solicitante=admin_user.email,
                activo_id=activo.id,
                asignado_a_id=admin_user.id
            )
            db.session.add(solicitud)
        
        # Confirmar cambios
        db.session.commit()
        
        print("✅ Datos de prueba creados exitosamente:")
        print(f"   📁 Categoría: {categoria.nombre}")
        print(f"   🏭 Activo: {activo.nombre} ({activo.codigo})")
        print(f"   📋 Solicitudes: {len(solicitudes)} creadas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        db.session.rollback()
        return False

def main():
    """Función principal"""
    print("🚀 Creando datos de prueba")
    print("=" * 40)
    
    # Crear aplicación Flask
    app = create_app()
    
    with app.app_context():
        crear_datos_prueba()

if __name__ == "__main__":
    main()