#!/usr/bin/env python3
"""
Script para eliminar datos de prueba/demo del sistema GMAO en producción
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.factory import create_app
from app.extensions import db
from app.models.inventario import Inventario
from app.models.usuario import Usuario
from app.models.orden_recambio import OrdenRecambio
from app.models.movimiento_inventario import MovimientoInventario
from sqlalchemy import text
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def identificar_datos_demo():
    """Identificar todos los datos de prueba en el sistema"""
    logger.info("🔍 Identificando datos de prueba...")
    
    datos_demo = {
        'inventario': [],
        'usuarios': [],
        'proveedores': []
    }
    
    # Artículos de inventario de demo (basado en códigos conocidos)
    codigos_demo = ['ART-001', 'ART-002', 'ART-003']
    
    for codigo in codigos_demo:
        articulo = Inventario.query.filter_by(codigo=codigo).first()
        if articulo:
            datos_demo['inventario'].append({
                'id': articulo.id,
                'codigo': articulo.codigo,
                'descripcion': articulo.descripcion or 'Sin descripción'
            })
    
    # Buscar otros artículos que puedan ser de demo por descripción o nombre
    articulos_sospechosos = Inventario.query.filter(
        db.or_(
            Inventario.descripcion.ilike('%demo%'),
            Inventario.descripcion.ilike('%prueba%'),
            Inventario.descripcion.ilike('%test%'),
            Inventario.nombre.ilike('%demo%') if hasattr(Inventario, 'nombre') else False,
            Inventario.nombre.ilike('%prueba%') if hasattr(Inventario, 'nombre') else False,
            Inventario.nombre.ilike('%test%') if hasattr(Inventario, 'nombre') else False,
            Inventario.codigo.ilike('%DEMO%'),
            Inventario.codigo.ilike('%TEST%'),
            Inventario.codigo.ilike('%PRUEBA%')
        )
    ).all()
    
    for articulo in articulos_sospechosos:
        if articulo.codigo not in [item['codigo'] for item in datos_demo['inventario']]:
            datos_demo['inventario'].append({
                'id': articulo.id,
                'codigo': articulo.codigo,
                'descripcion': articulo.descripcion or 'Sin descripción'
            })
    
    # Usuarios de demo
    usuarios_demo = Usuario.query.filter(
        db.or_(
            Usuario.username.ilike('%demo%'),
            Usuario.username.ilike('%test%'),
            Usuario.username.ilike('%prueba%'),
            Usuario.nombre.ilike('%demo%'),
            Usuario.nombre.ilike('%test%'),
            Usuario.nombre.ilike('%prueba%'),
            Usuario.email.ilike('%demo%'),
            Usuario.email.ilike('%test%'),
            Usuario.email.ilike('%prueba%')
        )
    ).all()
    
    for usuario in usuarios_demo:
        if usuario.username != 'admin':  # Nunca eliminar admin
            datos_demo['usuarios'].append({
                'id': usuario.id,
                'username': usuario.username,
                'nombre': usuario.nombre,
                'email': usuario.email
            })
    
    return datos_demo

def eliminar_movimientos_inventario(inventario_ids):
    """Eliminar movimientos de inventario relacionados con artículos demo"""
    if not inventario_ids:
        return 0
    
    logger.info(f"🗑️  Eliminando movimientos de inventario para {len(inventario_ids)} artículos...")
    
    # Eliminar movimientos
    count = MovimientoInventario.query.filter(
        MovimientoInventario.inventario_id.in_(inventario_ids)
    ).count()
    
    MovimientoInventario.query.filter(
        MovimientoInventario.inventario_id.in_(inventario_ids)
    ).delete(synchronize_session=False)
    
    return count

def eliminar_recambios_ordenes(inventario_ids):
    """Eliminar recambios de órdenes que usen artículos demo"""
    if not inventario_ids:
        return 0
    
    logger.info(f"🗑️  Eliminando recambios de órdenes para {len(inventario_ids)} artículos...")
    
    # Eliminar recambios de órdenes
    count = OrdenRecambio.query.filter(
        OrdenRecambio.inventario_id.in_(inventario_ids)
    ).count()
    
    OrdenRecambio.query.filter(
        OrdenRecambio.inventario_id.in_(inventario_ids)
    ).delete(synchronize_session=False)
    
    return count

def eliminar_datos_demo(datos_demo, dry_run=True):
    """Eliminar los datos de demo identificados"""
    if dry_run:
        logger.info("🧪 MODO DRY RUN - Solo mostrando lo que se eliminaría...")
    else:
        logger.info("🔥 ELIMINANDO datos de prueba...")
    
    resultados = {
        'inventario_eliminado': 0,
        'usuarios_eliminados': 0,
        'movimientos_eliminados': 0,
        'recambios_eliminados': 0
    }
    
    try:
        # Obtener IDs de inventario para eliminar dependencias
        inventario_ids = [item['id'] for item in datos_demo['inventario']]
        
        if not dry_run and inventario_ids:
            # Eliminar dependencias primero
            resultados['movimientos_eliminados'] = eliminar_movimientos_inventario(inventario_ids)
            resultados['recambios_eliminados'] = eliminar_recambios_ordenes(inventario_ids)
        
        # Eliminar artículos de inventario
        for item in datos_demo['inventario']:
            logger.info(f"  📦 Inventario: {item['codigo']} - {item['descripcion']}")
            if not dry_run:
                Inventario.query.filter_by(id=item['id']).delete()
                resultados['inventario_eliminado'] += 1
        
        # Eliminar usuarios demo (excepto admin)
        for item in datos_demo['usuarios']:
            if item['username'] != 'admin':
                logger.info(f"  👤 Usuario: {item['username']} - {item['nombre']}")
                if not dry_run:
                    Usuario.query.filter_by(id=item['id']).delete()
                    resultados['usuarios_eliminados'] += 1
        
        if not dry_run:
            db.session.commit()
            logger.info("✅ Datos de prueba eliminados correctamente")
        else:
            logger.info("✅ Revisión completada - use --execute para eliminar realmente")
        
        return resultados
        
    except Exception as e:
        if not dry_run:
            db.session.rollback()
        logger.error(f"❌ Error durante la eliminación: {e}")
        raise

def main():
    """Función principal"""
    app = create_app()
    
    with app.app_context():
        # Verificar argumentos
        dry_run = '--execute' not in sys.argv
        
        if dry_run:
            print("🧪 MODO DRY RUN - Para eliminar realmente, use: python clean_demo_data.py --execute")
        else:
            print("🔥 MODO EJECUCIÓN - Se eliminarán los datos de prueba")
            
            # Confirmación adicional
            confirm = input("¿Está seguro de que desea eliminar todos los datos de prueba? (escriba 'CONFIRMAR'): ")
            if confirm != 'CONFIRMAR':
                print("❌ Operación cancelada")
                return
        
        print()
        
        # Identificar datos de demo
        datos_demo = identificar_datos_demo()
        
        # Mostrar resumen
        print(f"📊 RESUMEN DE DATOS DE PRUEBA ENCONTRADOS:")
        print(f"   - Artículos de inventario: {len(datos_demo['inventario'])}")
        print(f"   - Usuarios: {len(datos_demo['usuarios'])}")
        print()
        
        if not any(datos_demo.values()):
            print("✅ No se encontraron datos de prueba para eliminar")
            return
        
        # Eliminar datos
        resultados = eliminar_datos_demo(datos_demo, dry_run=dry_run)
        
        if not dry_run:
            print(f"\n📊 RESULTADOS:")
            print(f"   - Artículos eliminados: {resultados['inventario_eliminado']}")
            print(f"   - Usuarios eliminados: {resultados['usuarios_eliminados']}")
            print(f"   - Movimientos eliminados: {resultados['movimientos_eliminados']}")
            print(f"   - Recambios eliminados: {resultados['recambios_eliminados']}")

if __name__ == "__main__":
    main()