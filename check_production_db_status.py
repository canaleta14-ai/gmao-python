#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# Configurar variables de entorno para producción
os.environ['SECRET_KEY'] = 'gmao-production-check-key-temp-2025'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'mantenimiento-470311'

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.extensions import db
from app.models.usuario import Usuario
from sqlalchemy import text, inspect

def check_production_database():
    """Verificar el estado actual de la base de datos de producción"""
    
    print("=== VERIFICACIÓN COMPLETA DE BASE DE DATOS DE PRODUCCIÓN ===\n")
    
    try:
        # Crear la aplicación
        print("🏗️ Conectando a la aplicación de producción...")
        app = create_app()
        
        with app.app_context():
            print("🗄️ Verificando base de datos de producción...\n")
            
            # Verificar usuarios
            print("👥 USUARIOS EN LA BASE DE DATOS:")
            try:
                usuarios = Usuario.query.all()
                print(f"   📊 Total de usuarios: {len(usuarios)}")
                
                if usuarios:
                    print("   📋 Lista completa de usuarios:")
                    for i, user in enumerate(usuarios, 1):
                        print(f"   {i}. Usuario: {user.username}")
                        print(f"      Email: {user.email}")
                        print(f"      Nombre: {user.nombre}")
                        print(f"      Rol: {user.rol}")
                        print(f"      Activo: {user.activo}")
                        print(f"      ID: {user.id}")
                        if hasattr(user, 'fecha_creacion'):
                            print(f"      Fecha creación: {user.fecha_creacion}")
                        print()
                else:
                    print("   ✅ No hay usuarios en la base de datos")
                    
            except Exception as e:
                print(f"   ❌ Error consultando usuarios: {e}")
            
            # Verificar todas las tablas usando inspector
            print("🗂️ VERIFICANDO TODAS LAS TABLAS:")
            
            try:
                inspector = inspect(db.engine)
                table_names = inspector.get_table_names()
                print(f"   📊 Total de tablas encontradas: {len(table_names)}")
                print(f"   📋 Tablas: {', '.join(table_names)}")
                print()
                
                total_records = 0
                
                for table_name in table_names:
                    try:
                        # Usar text() para consultas SQL directas
                        result = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                        count = result.scalar()
                        total_records += count
                        
                        if count > 0:
                            print(f"   📋 Tabla '{table_name}': {count} registros")
                            
                            # Mostrar algunos registros de ejemplo para tablas con datos
                            if count <= 10:
                                try:
                                    sample_result = db.session.execute(text(f"SELECT * FROM {table_name} LIMIT 3"))
                                    columns = sample_result.keys()
                                    rows = sample_result.fetchall()
                                    
                                    print(f"      📄 Columnas: {', '.join(columns)}")
                                    for j, row in enumerate(rows, 1):
                                        print(f"      {j}. {dict(zip(columns, row))}")
                                    print()
                                except Exception as e:
                                    print(f"      ⚠️ Error mostrando datos: {e}")
                        else:
                            print(f"   📋 Tabla '{table_name}': 0 registros (vacía)")
                            
                    except Exception as e:
                        print(f"   ⚠️ Error contando tabla '{table_name}': {e}")
                
                print(f"\n📊 RESUMEN TOTAL: {total_records} registros en todas las tablas")
                            
            except Exception as e:
                print(f"   ❌ Error verificando tablas: {e}")
                import traceback
                traceback.print_exc()
            
            # Verificar modelos específicos si existen
            print("\n🔍 VERIFICANDO MODELOS ESPECÍFICOS:")
            
            try:
                # Intentar importar y verificar otros modelos
                try:
                    from app.models.activo import Activo
                    activos_count = Activo.query.count()
                    print(f"   🏭 Activos: {activos_count}")
                    if activos_count > 0:
                        activos_sample = Activo.query.limit(3).all()
                        for activo in activos_sample:
                            print(f"      - {activo.codigo}: {activo.nombre}")
                except ImportError:
                    print("   ℹ️ Modelo Activo no disponible")
                except Exception as e:
                    print(f"   ⚠️ Error verificando activos: {e}")
                
                # Verificar si hay tablas de órdenes, planes, etc.
                for model_table in ['ordenes_trabajo', 'planes_mantenimiento', 'movimientos', 'solicitudes']:
                    try:
                        result = db.session.execute(text(f"SELECT COUNT(*) FROM {model_table}"))
                        count = result.scalar()
                        print(f"   📋 {model_table}: {count} registros")
                    except Exception:
                        print(f"   ℹ️ Tabla {model_table} no existe")
                        
            except Exception as e:
                print(f"   ⚠️ Error verificando modelos específicos: {e}")
            
            print("\n" + "="*60)
            
            # Determinar si la base de datos está realmente limpia
            if len(usuarios) > 1:
                print("🚨 PROBLEMA DETECTADO:")
                print(f"   La base de datos contiene {len(usuarios)} usuarios")
                print("   Se esperaba únicamente 1 usuario (admin)")
                print("   🔴 LA BASE DE DATOS NO ESTÁ LIMPIA")
                return False
            elif len(usuarios) == 1:
                admin = usuarios[0]
                if admin.username == 'admin' and admin.email == 'admin@gmao.com':
                    if total_records <= 1:  # Solo el usuario admin
                        print("✅ BASE DE DATOS COMPLETAMENTE LIMPIA:")
                        print("   Solo contiene el usuario administrador")
                        print("   No hay otros datos en ninguna tabla")
                        return True
                    else:
                        print("🚨 PROBLEMA DETECTADO:")
                        print("   Aunque solo hay 1 usuario admin,")
                        print(f"   existen {total_records} registros totales en la BD")
                        print("   🔴 LA BASE DE DATOS CONTIENE DATOS ANTIGUOS")
                        return False
                else:
                    print("🚨 PROBLEMA DETECTADO:")
                    print("   El único usuario no es el administrador esperado")
                    print(f"   Usuario encontrado: {admin.username} ({admin.email})")
                    return False
            else:
                print("🚨 PROBLEMA DETECTADO:")
                print("   La base de datos está vacía (sin usuarios)")
                return False
                
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        is_clean = check_production_database()
        if is_clean:
            print("\n🎉 La base de datos está completamente limpia.")
        else:
            print("\n❌ La base de datos requiere limpieza completa.")
            print("💡 Recomendación: Eliminar y recrear la base de datos")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()