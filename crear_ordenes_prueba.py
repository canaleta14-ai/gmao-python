#!/usr/bin/env python3
"""
Script para crear órdenes de trabajo de prueba para el dashboard.
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio de la aplicación al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.factory import create_app
from app.models.orden_trabajo import OrdenTrabajo
from app.models.activo import Activo
from app.models.usuario import Usuario

def crear_ordenes_prueba():
    """Crear órdenes de trabajo de prueba con diferentes estados"""
    app = create_app()
    
    with app.app_context():
        from app.extensions import db
        
        # Verificar que existan activos y usuarios
        activo = Activo.query.first()
        if not activo:
            print("❌ No hay activos en la base de datos. Creando activo de prueba...")
            activo = Activo(
                codigo="ACT-001",
                nombre="Equipo de Prueba",
                descripcion="Activo creado para pruebas del dashboard",
                categoria="Equipos",
                ubicacion="Planta Principal",
                estado="Activo"
            )
            db.session.add(activo)
            db.session.commit()
            print(f"✅ Activo creado: {activo.nombre}")
        
        usuario = Usuario.query.first()
        if not usuario:
            print("❌ No hay usuarios en la base de datos. Creando usuario de prueba...")
            usuario = Usuario(
                username="admin",
                email="admin@gmao.com",
                nombre="Administrador Sistema",
                rol="admin",
                activo=True
            )
            usuario.set_password("admin123")
            db.session.add(usuario)
            db.session.commit()
            print(f"✅ Usuario creado: {usuario.username}")
        
        # Crear órdenes con diferentes estados
        ordenes_crear = [
            {
                "numero_orden": "OT-001",
                "tipo": "Mantenimiento Preventivo",
                "estado": "Pendiente",
                "prioridad": "Alta",
                "descripcion": "Revisión mensual del equipo principal",
                "fecha_creacion": datetime.now() - timedelta(days=2)
            },
            {
                "numero_orden": "OT-002",
                "tipo": "Mantenimiento Correctivo",
                "estado": "En Progreso",
                "prioridad": "Media",
                "descripcion": "Reparación de falla en motor",
                "fecha_creacion": datetime.now() - timedelta(days=1)
            },
            {
                "numero_orden": "OT-003",
                "tipo": "Mantenimiento Preventivo",
                "estado": "Completada",
                "prioridad": "Baja",
                "descripcion": "Lubricación de componentes",
                "fecha_creacion": datetime.now(),
                "fecha_completada": datetime.now()
            },
            {
                "numero_orden": "OT-004",
                "tipo": "Inspección",
                "estado": "Pendiente",
                "prioridad": "Media",
                "descripcion": "Inspección de seguridad trimestral",
                "fecha_creacion": datetime.now() - timedelta(hours=6)
            },
            {
                "numero_orden": "OT-005",
                "tipo": "Mantenimiento Correctivo",
                "estado": "Cancelada",
                "prioridad": "Baja",
                "descripcion": "Orden cancelada por cambio de prioridades",
                "fecha_creacion": datetime.now() - timedelta(days=3)
            },
            {
                "numero_orden": "OT-006",
                "tipo": "Mantenimiento Preventivo",
                "estado": "Completada",
                "prioridad": "Alta",
                "descripcion": "Cambio de filtros programado",
                "fecha_creacion": datetime.now(),
                "fecha_completada": datetime.now()
            }
        ]
        
        ordenes_creadas = 0
        
        for orden_data in ordenes_crear:
            # Verificar si ya existe una orden con ese número
            orden_existente = OrdenTrabajo.query.filter_by(numero_orden=orden_data["numero_orden"]).first()
            if orden_existente:
                print(f"⚠️  Orden {orden_data['numero_orden']} ya existe, saltando...")
                continue
            
            orden = OrdenTrabajo(
                numero_orden=orden_data["numero_orden"],
                tipo=orden_data["tipo"],
                estado=orden_data["estado"],
                prioridad=orden_data["prioridad"],
                descripcion=orden_data["descripcion"],
                activo_id=activo.id,
                tecnico_id=usuario.id,
                fecha_creacion=orden_data["fecha_creacion"]
            )
            
            if "fecha_completada" in orden_data:
                orden.fecha_completada = orden_data["fecha_completada"]
            
            db.session.add(orden)
            ordenes_creadas += 1
            print(f"✅ Orden creada: {orden_data['numero_orden']} - {orden_data['estado']}")
        
        try:
            db.session.commit()
            print(f"\n🎉 {ordenes_creadas} órdenes de trabajo creadas exitosamente!")
            
            # Mostrar estadísticas
            print("\n📊 ESTADÍSTICAS ACTUALES:")
            total_ordenes = OrdenTrabajo.query.count()
            pendientes = OrdenTrabajo.query.filter_by(estado='Pendiente').count()
            en_progreso = OrdenTrabajo.query.filter_by(estado='En Progreso').count()
            completadas = OrdenTrabajo.query.filter_by(estado='Completada').count()
            canceladas = OrdenTrabajo.query.filter_by(estado='Cancelada').count()
            
            print(f"   Total de órdenes: {total_ordenes}")
            print(f"   Pendientes: {pendientes}")
            print(f"   En Progreso: {en_progreso}")
            print(f"   Completadas: {completadas}")
            print(f"   Canceladas: {canceladas}")
            print(f"   Activas (Pendientes + En Progreso): {pendientes + en_progreso}")
            
            # Completadas hoy
            hoy = datetime.now().date()
            completadas_hoy = OrdenTrabajo.query.filter(
                OrdenTrabajo.estado == 'Completada',
                OrdenTrabajo.fecha_completada >= hoy
            ).count()
            print(f"   Completadas hoy: {completadas_hoy}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear órdenes: {str(e)}")
            return False
        
        return True

def main():
    print("=== CREACIÓN DE ÓRDENES DE PRUEBA PARA DASHBOARD ===\n")
    
    if crear_ordenes_prueba():
        print("\n✅ Órdenes de prueba creadas exitosamente!")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. El dashboard ahora debería mostrar estadísticas")
        print("2. Puedes acceder al dashboard en: /dashboard")
        print("3. Las órdenes aparecerán en la sección de órdenes: /ordenes")
        print("\n🚀 ¡El sistema está listo para usar!")
    else:
        print("\n❌ Error al crear órdenes de prueba")

if __name__ == "__main__":
    main()