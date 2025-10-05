#!/usr/bin/env python3
"""
Script para probar la funcionalidad de eliminación de órdenes de trabajo.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio de la aplicación al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.factory import create_app
from app.models.orden_trabajo import OrdenTrabajo
from app.models.activo import Activo
from app.models.usuario import Usuario

def crear_orden_prueba():
    """Crear una orden de prueba para eliminar"""
    app = create_app()
    
    with app.app_context():
        # Buscar un activo existente
        activo = Activo.query.first()
        if not activo:
            print("❌ No hay activos en la base de datos")
            return None
        
        # Buscar un usuario existente
        usuario = Usuario.query.first()
        if not usuario:
            print("❌ No hay usuarios en la base de datos")
            return None
        
        # Crear orden de prueba
        orden = OrdenTrabajo(
            numero_orden=f"TEST-ELIMINAR-{len(OrdenTrabajo.query.all()) + 1}",
            tipo="Mantenimiento Correctivo",
            estado="Pendiente",
            prioridad="Media",
            descripcion="Orden de prueba para eliminar",
            activo_id=activo.id,
            usuario_id=usuario.id
        )
        
        from app.extensions import db
        db.session.add(orden)
        db.session.commit()
        
        print(f"✅ Orden de prueba creada: #{orden.id} ({orden.numero_orden})")
        return orden.id

def probar_eliminacion_local():
    """Probar la eliminación usando la API local"""
    app = create_app()
    
    with app.app_context():
        # Buscar una orden pendiente
        orden = OrdenTrabajo.query.filter_by(estado='Pendiente').first()
        
        if not orden:
            print("❌ No hay órdenes pendientes para eliminar")
            return False
        
        print(f"🔍 Probando eliminación de orden #{orden.id} ({orden.numero_orden})")
        
        # Simular eliminación
        try:
            from app.controllers.ordenes_controller import eliminar_orden
            resultado = eliminar_orden(orden.id)
            print(f"✅ Eliminación exitosa: {resultado}")
            return True
        except Exception as e:
            print(f"❌ Error en eliminación: {str(e)}")
            return False

def verificar_endpoint_api():
    """Verificar que el endpoint de eliminación esté disponible"""
    print("\n🌐 Verificando endpoint de eliminación en producción...")
    
    # URL de la aplicación en producción
    base_url = "https://gmao-sistema-2025.ew.r.appspot.com"
    
    try:
        # Intentar acceder a la página de órdenes
        response = requests.get(f"{base_url}/ordenes", timeout=10)
        if response.status_code == 200:
            print("✅ Aplicación accesible en producción")
            
            # Verificar si el JavaScript contiene las funciones de eliminación
            if "mostrarModalEliminarOrden" in response.text:
                print("✅ Función JavaScript de eliminación encontrada")
            else:
                print("❌ Función JavaScript de eliminación NO encontrada")
            
            if "modalEliminarOrden" in response.text:
                print("✅ Modal de eliminación encontrado en HTML")
            else:
                print("❌ Modal de eliminación NO encontrado en HTML")
                
        else:
            print(f"❌ Error accediendo a la aplicación: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")

def main():
    print("=== PRUEBA DE FUNCIONALIDAD DE ELIMINACIÓN ===\n")
    
    # 1. Verificar órdenes existentes
    print("1. Verificando órdenes existentes...")
    app = create_app()
    with app.app_context():
        ordenes_pendientes = OrdenTrabajo.query.filter_by(estado='Pendiente').count()
        ordenes_canceladas = OrdenTrabajo.query.filter_by(estado='Cancelada').count()
        print(f"   Órdenes Pendientes: {ordenes_pendientes}")
        print(f"   Órdenes Canceladas: {ordenes_canceladas}")
        print(f"   Total eliminables: {ordenes_pendientes + ordenes_canceladas}")
    
    # 2. Crear orden de prueba si es necesario
    if ordenes_pendientes == 0:
        print("\n2. Creando orden de prueba...")
        crear_orden_prueba()
    else:
        print("\n2. Ya hay órdenes pendientes disponibles")
    
    # 3. Probar eliminación local
    print("\n3. Probando eliminación local...")
    probar_eliminacion_local()
    
    # 4. Verificar endpoint en producción
    print("\n4. Verificando endpoint en producción...")
    verificar_endpoint_api()
    
    print("\n=== PRUEBA COMPLETADA ===")
    print("\n📋 INSTRUCCIONES PARA PROBAR EN EL NAVEGADOR:")
    print("1. Ve a: https://gmao-sistema-2025.ew.r.appspot.com/ordenes")
    print("2. Busca órdenes con estado 'Pendiente' o 'Cancelada'")
    print("3. Deberías ver un botón rojo con icono de papelera en la columna 'Acciones'")
    print("4. Haz clic en el botón para probar la eliminación")

if __name__ == "__main__":
    main()