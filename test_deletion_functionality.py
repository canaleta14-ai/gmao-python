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

def test_deletion_functionality():
    """Probar la funcionalidad de eliminación de diferentes modelos"""
    app = create_app()
    
    with app.app_context():
        print("=== PRUEBA DE FUNCIONALIDAD DE ELIMINACIÓN ===\n")
        
        # Estado inicial
        print("📊 Estado inicial de la base de datos:")
        usuarios_count = Usuario.query.count()
        categorias_count = Categoria.query.count()
        activos_count = Activo.query.count()
        solicitudes_count = SolicitudServicio.query.count()
        
        print(f"   - Usuarios: {usuarios_count}")
        print(f"   - Categorías: {categorias_count}")
        print(f"   - Activos: {activos_count}")
        print(f"   - Solicitudes: {solicitudes_count}")
        print()
        
        # Test 1: Eliminar una solicitud de servicio
        print("🗑️ Test 1: Eliminando una solicitud de servicio...")
        try:
            solicitud_test = SolicitudServicio.query.filter_by(numero_solicitud='SOL-TEST-001').first()
            if solicitud_test:
                print(f"   Eliminando solicitud: {solicitud_test.titulo}")
                db.session.delete(solicitud_test)
                db.session.commit()
                print("   ✅ Solicitud eliminada exitosamente")
            else:
                print("   ❌ No se encontró la solicitud de prueba")
        except Exception as e:
            print(f"   ❌ Error eliminando solicitud: {e}")
            db.session.rollback()
        
        # Verificar eliminación
        solicitudes_after = SolicitudServicio.query.count()
        print(f"   Solicitudes después de eliminación: {solicitudes_after}")
        print()
        
        # Test 2: Intentar eliminar un activo (debería fallar si tiene solicitudes relacionadas)
        print("🗑️ Test 2: Intentando eliminar un activo con solicitudes relacionadas...")
        try:
            activo_test = Activo.query.filter_by(codigo='000-TEST-00001').first()
            if activo_test:
                # Verificar si tiene solicitudes relacionadas
                solicitudes_relacionadas = SolicitudServicio.query.filter_by(activo_id=activo_test.id).count()
                print(f"   Activo encontrado: {activo_test.nombre}")
                print(f"   Solicitudes relacionadas: {solicitudes_relacionadas}")
                
                if solicitudes_relacionadas > 0:
                    print("   ⚠️ El activo tiene solicitudes relacionadas. Esto debería fallar o requerir eliminación en cascada.")
                
                # Intentar eliminar
                db.session.delete(activo_test)
                db.session.commit()
                print("   ✅ Activo eliminado exitosamente")
            else:
                print("   ❌ No se encontró el activo de prueba")
        except Exception as e:
            print(f"   ❌ Error eliminando activo (esperado si hay restricciones FK): {e}")
            db.session.rollback()
        
        # Verificar estado del activo
        activos_after = Activo.query.count()
        print(f"   Activos después de intento de eliminación: {activos_after}")
        print()
        
        # Test 3: Eliminar solicitudes restantes relacionadas al activo
        print("🗑️ Test 3: Eliminando solicitudes restantes relacionadas al activo...")
        try:
            activo_test = Activo.query.filter_by(codigo='000-TEST-00001').first()
            if activo_test:
                solicitudes_relacionadas = SolicitudServicio.query.filter_by(activo_id=activo_test.id).all()
                print(f"   Encontradas {len(solicitudes_relacionadas)} solicitudes relacionadas")
                
                for solicitud in solicitudes_relacionadas:
                    print(f"   Eliminando: {solicitud.numero_solicitud}")
                    db.session.delete(solicitud)
                
                db.session.commit()
                print("   ✅ Solicitudes relacionadas eliminadas exitosamente")
            else:
                print("   ❌ No se encontró el activo de prueba")
        except Exception as e:
            print(f"   ❌ Error eliminando solicitudes relacionadas: {e}")
            db.session.rollback()
        
        # Test 4: Ahora intentar eliminar el activo sin solicitudes relacionadas
        print("🗑️ Test 4: Eliminando activo sin solicitudes relacionadas...")
        try:
            activo_test = Activo.query.filter_by(codigo='000-TEST-00001').first()
            if activo_test:
                print(f"   Eliminando activo: {activo_test.nombre}")
                db.session.delete(activo_test)
                db.session.commit()
                print("   ✅ Activo eliminado exitosamente")
            else:
                print("   ❌ No se encontró el activo de prueba")
        except Exception as e:
            print(f"   ❌ Error eliminando activo: {e}")
            db.session.rollback()
        
        # Test 5: Eliminar categoría
        print("🗑️ Test 5: Eliminando categoría...")
        try:
            categoria_test = Categoria.query.filter_by(nombre='Equipos de Prueba').first()
            if categoria_test:
                print(f"   Eliminando categoría: {categoria_test.nombre}")
                db.session.delete(categoria_test)
                db.session.commit()
                print("   ✅ Categoría eliminada exitosamente")
            else:
                print("   ❌ No se encontró la categoría de prueba")
        except Exception as e:
            print(f"   ❌ Error eliminando categoría: {e}")
            db.session.rollback()
        
        # Estado final
        print("\n📊 Estado final de la base de datos:")
        usuarios_final = Usuario.query.count()
        categorias_final = Categoria.query.count()
        activos_final = Activo.query.count()
        solicitudes_final = SolicitudServicio.query.count()
        
        print(f"   - Usuarios: {usuarios_final}")
        print(f"   - Categorías: {categorias_final}")
        print(f"   - Activos: {activos_final}")
        print(f"   - Solicitudes: {solicitudes_final}")
        
        # Resumen de cambios
        print("\n📈 Resumen de cambios:")
        print(f"   - Usuarios: {usuarios_count} → {usuarios_final} (Δ: {usuarios_final - usuarios_count})")
        print(f"   - Categorías: {categorias_count} → {categorias_final} (Δ: {categorias_final - categorias_count})")
        print(f"   - Activos: {activos_count} → {activos_final} (Δ: {activos_final - activos_count})")
        print(f"   - Solicitudes: {solicitudes_count} → {solicitudes_final} (Δ: {solicitudes_final - solicitudes_count})")
        
        print("\n✅ Prueba de funcionalidad de eliminación completada.")

if __name__ == "__main__":
    try:
        test_deletion_functionality()
    except Exception as e:
        print(f"❌ Error en prueba de eliminación: {e}")
        import traceback
        traceback.print_exc()