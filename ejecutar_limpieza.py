#!/usr/bin/env python3
"""
Script directo para eliminar datos de prueba - ejecuta dentro del contexto de Flask
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.factory import create_app
from app.extensions import db
from app.models.inventario import Inventario
from app.models.usuario import Usuario
from app.models.orden_recambio import OrdenRecambio
from app.models.movimiento_inventario import MovimientoInventario
from sqlalchemy import text

def ejecutar_limpieza():
    """Ejecutar limpieza de datos de prueba"""
    
    # Crear aplicación Flask
    app = create_app()
    
    with app.app_context():
        print("🔍 Iniciando limpieza de datos de prueba...")
        print("=" * 50)
        
        try:
            # 1. Identificar artículos de prueba
            codigos_demo = ['ART-001', 'ART-002', 'ART-003']
            articulos_demo = []
            
            print("📦 Buscando artículos de prueba...")
            for codigo in codigos_demo:
                articulo = Inventario.query.filter_by(codigo=codigo).first()
                if articulo:
                    articulos_demo.append(articulo)
                    print(f"  ✓ Encontrado: {codigo} - {articulo.descripcion}")
            
            # Buscar otros artículos sospechosos
            try:
                otros_articulos = Inventario.query.filter(
                    db.or_(
                        Inventario.descripcion.ilike('%demo%'),
                        Inventario.descripcion.ilike('%prueba%'),
                        Inventario.descripcion.ilike('%test%'),
                        Inventario.codigo.ilike('%DEMO%'),
                        Inventario.codigo.ilike('%TEST%'),
                        Inventario.codigo.ilike('%PRUEBA%')
                    )
                ).all()
                
                for articulo in otros_articulos:
                    if articulo not in articulos_demo:
                        articulos_demo.append(articulo)
                        print(f"  ✓ Encontrado (sospechoso): {articulo.codigo} - {articulo.descripcion}")
            except Exception as e:
                print(f"  ⚠️ Error buscando artículos sospechosos: {e}")
            
            # 2. Identificar usuarios de prueba
            print("\n👤 Buscando usuarios de prueba...")
            usuarios_demo = []
            
            try:
                usuarios_sospechosos = Usuario.query.filter(
                    db.and_(
                        Usuario.username != 'admin',
                        db.or_(
                            Usuario.username.ilike('%demo%'),
                            Usuario.username.ilike('%test%'),
                            Usuario.username.ilike('%prueba%'),
                            Usuario.nombre.ilike('%demo%'),
                            Usuario.nombre.ilike('%test%'),
                            Usuario.nombre.ilike('%prueba%')
                        )
                    )
                ).all()
                
                for usuario in usuarios_sospechosos:
                    usuarios_demo.append(usuario)
                    print(f"  ✓ Encontrado: {usuario.username} - {usuario.nombre}")
            except Exception as e:
                print(f"  ⚠️ Error buscando usuarios demo: {e}")
            
            # 3. Mostrar resumen
            print(f"\n📊 RESUMEN:")
            print(f"  - Artículos a eliminar: {len(articulos_demo)}")
            print(f"  - Usuarios a eliminar: {len(usuarios_demo)}")
            
            if not articulos_demo and not usuarios_demo:
                print("\n✅ No se encontraron datos de prueba para eliminar.")
                return
            
            print(f"\n🔥 ELIMINANDO DATOS DE PRUEBA...")
            print("-" * 30)
            
            resultados = {
                'articulos_eliminados': 0,
                'usuarios_eliminados': 0,
                'movimientos_eliminados': 0,
                'recambios_eliminados': 0
            }
            
            # 4. Eliminar dependencias de artículos
            if articulos_demo:
                inventario_ids = [art.id for art in articulos_demo]
                
                # Eliminar recambios de órdenes
                print("🗑️ Eliminando recambios de órdenes...")
                try:
                    recambios_count = OrdenRecambio.query.filter(
                        OrdenRecambio.inventario_id.in_(inventario_ids)
                    ).count()
                    
                    if recambios_count > 0:
                        OrdenRecambio.query.filter(
                            OrdenRecambio.inventario_id.in_(inventario_ids)
                        ).delete(synchronize_session=False)
                        resultados['recambios_eliminados'] = recambios_count
                        print(f"  ✓ {recambios_count} recambios eliminados")
                    else:
                        print("  ✓ No hay recambios que eliminar")
                except Exception as e:
                    print(f"  ⚠️ Error eliminando recambios: {e}")
                
                # Eliminar movimientos de inventario
                print("🗑️ Eliminando movimientos de inventario...")
                try:
                    movimientos_count = MovimientoInventario.query.filter(
                        MovimientoInventario.inventario_id.in_(inventario_ids)
                    ).count()
                    
                    if movimientos_count > 0:
                        MovimientoInventario.query.filter(
                            MovimientoInventario.inventario_id.in_(inventario_ids)
                        ).delete(synchronize_session=False)
                        resultados['movimientos_eliminados'] = movimientos_count
                        print(f"  ✓ {movimientos_count} movimientos eliminados")
                    else:
                        print("  ✓ No hay movimientos que eliminar")
                except Exception as e:
                    print(f"  ⚠️ Error eliminando movimientos: {e}")
            
            # 5. Eliminar artículos de inventario
            print("🗑️ Eliminando artículos de inventario...")
            for articulo in articulos_demo:
                try:
                    print(f"  - Eliminando: {articulo.codigo}")
                    db.session.delete(articulo)
                    resultados['articulos_eliminados'] += 1
                except Exception as e:
                    print(f"  ⚠️ Error eliminando {articulo.codigo}: {e}")
            
            # 6. Eliminar usuarios de prueba
            print("🗑️ Eliminando usuarios de prueba...")
            for usuario in usuarios_demo:
                try:
                    print(f"  - Eliminando: {usuario.username}")
                    db.session.delete(usuario)
                    resultados['usuarios_eliminados'] += 1
                except Exception as e:
                    print(f"  ⚠️ Error eliminando {usuario.username}: {e}")
            
            # 7. Commit de todos los cambios
            print("\n💾 Guardando cambios...")
            db.session.commit()
            print("✅ Cambios guardados exitosamente")
            
            # 8. Mostrar resultados finales
            print(f"\n🎉 LIMPIEZA COMPLETADA")
            print("=" * 30)
            print(f"✓ Artículos eliminados: {resultados['articulos_eliminados']}")
            print(f"✓ Usuarios eliminados: {resultados['usuarios_eliminados']}")
            print(f"✓ Movimientos eliminados: {resultados['movimientos_eliminados']}")
            print(f"✓ Recambios eliminados: {resultados['recambios_eliminados']}")
            print(f"\n🧹 Datos de prueba eliminados correctamente de producción")
            
        except Exception as e:
            print(f"\n❌ ERROR durante la limpieza: {e}")
            print("🔄 Revertiendo cambios...")
            db.session.rollback()
            raise

if __name__ == "__main__":
    ejecutar_limpieza()