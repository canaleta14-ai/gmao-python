#!/usr/bin/env python3
"""
Script para limpiar la base de datos de producción
Elimina todos los datos de prueba manteniendo la estructura
"""

import os
import sys
from flask import Flask
from app.factory import create_app
from app.extensions import db
from app.models.solicitud_servicio import SolicitudServicio
from app.models.orden_trabajo import OrdenTrabajo
from app.models.activo import Activo
from app.models.usuario import Usuario
from app.models.proveedor import Proveedor
from app.models.archivo_adjunto import ArchivoAdjunto
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.inventario import Inventario
from app.models.movimiento_inventario import MovimientoInventario
from app.models.manual import Manual
from app.models.categoria import Categoria
from app.models.orden_recambio import OrdenRecambio
from app.models.control_generacion import ControlGeneracion
from sqlalchemy import text
import shutil

def verificar_estado_db():
    """Verifica el estado actual de la base de datos"""
    print("🔍 Verificando estado actual de la base de datos...")
    
    # Contar registros en cada tabla
    tablas = [
        (SolicitudServicio, "Solicitudes de Servicio"),
        (OrdenTrabajo, "Órdenes de Trabajo"),
        (Activo, "Activos"),
        (Usuario, "Usuarios"),
        (Proveedor, "Proveedores"),
        (ArchivoAdjunto, "Archivos Adjuntos"),
        (PlanMantenimiento, "Planes de Mantenimiento"),
        (Inventario, "Inventario"),
        (MovimientoInventario, "Movimientos de Inventario"),
        (Manual, "Manuales"),
        (Categoria, "Categorías"),
        (OrdenRecambio, "Órdenes de Recambio"),
        (ControlGeneracion, "Control de Generación")
    ]
    
    total_registros = 0
    for modelo, nombre in tablas:
        try:
            if modelo == PlanMantenimiento:
                # Usar consulta SQL directa para evitar problemas con el modelo
                result = db.session.execute(text("SELECT COUNT(*) FROM plan_mantenimiento"))
                count = result.scalar()
            else:
                count = modelo.query.count()
            print(f"  📊 {nombre}: {count} registros")
            total_registros += count
        except Exception as e:
            print(f"  ❌ Error al contar {nombre}: {e}")
            # Intentar con consulta SQL directa
            try:
                table_name = modelo.__tablename__
                result = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                print(f"  📊 {nombre} (SQL directo): {count} registros")
                total_registros += count
            except Exception as e2:
                print(f"  ❌ Error también con SQL directo para {nombre}: {e2}")
    
    print(f"\n📈 Total de registros en la base de datos: {total_registros}")
    return total_registros

def limpiar_archivos_uploads():
    """Limpia los archivos subidos"""
    print("\n🗂️ Limpiando archivos uploads...")
    
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        subdirs = ["solicitudes", "ordenes", "manuales"]
        for subdir in subdirs:
            subdir_path = os.path.join(uploads_dir, subdir)
            if os.path.exists(subdir_path):
                try:
                    # Eliminar contenido pero mantener la estructura
                    for item in os.listdir(subdir_path):
                        item_path = os.path.join(subdir_path, item)
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.remove(item_path)
                    print(f"  ✅ Limpiado: {subdir_path}")
                except Exception as e:
                    print(f"  ❌ Error limpiando {subdir_path}: {e}")
    
def limpiar_base_datos():
    """Limpia todos los datos de la base de datos manteniendo la estructura"""
    print("\n🧹 Iniciando limpieza de base de datos...")
    
    try:
        # Para SQLite, deshabilitar restricciones de clave foránea temporalmente
        db.session.execute(text("PRAGMA foreign_keys = OFF"))
        
        # Orden de eliminación (respetando dependencias)
        modelos_orden = [
            (MovimientoInventario, "Movimientos de Inventario"),
            (ArchivoAdjunto, "Archivos Adjuntos"),
            (OrdenRecambio, "Órdenes de Recambio"),
            (OrdenTrabajo, "Órdenes de Trabajo"),
            (SolicitudServicio, "Solicitudes de Servicio"),
            (PlanMantenimiento, "Planes de Mantenimiento"),
            (Inventario, "Inventario"),
            (Manual, "Manuales"),
            (Activo, "Activos"),
            (Categoria, "Categorías"),
            (ControlGeneracion, "Control de Generación"),
            (Proveedor, "Proveedores")
        ]
        
        for modelo, nombre in modelos_orden:
            try:
                # Contar registros antes de eliminar
                if modelo == PlanMantenimiento:
                    result = db.session.execute(text("SELECT COUNT(*) FROM plan_mantenimiento"))
                    count_antes = result.scalar()
                else:
                    count_antes = modelo.query.count()
                
                if count_antes > 0:
                    # Eliminar todos los registros
                    if modelo == PlanMantenimiento:
                        # Usar SQL directo para PlanMantenimiento
                        db.session.execute(text("DELETE FROM plan_mantenimiento"))
                    else:
                        modelo.query.delete()
                    print(f"  ✅ {nombre}: {count_antes} registros eliminados")
                else:
                    print(f"  ℹ️ {nombre}: Ya estaba vacía")
            except Exception as e:
                print(f"  ❌ Error eliminando {nombre}: {e}")
                # Intentar con SQL directo como fallback
                try:
                    table_name = modelo.__tablename__
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count_antes = result.scalar()
                    if count_antes > 0:
                        db.session.execute(text(f"DELETE FROM {table_name}"))
                        print(f"  ✅ {nombre} (SQL directo): {count_antes} registros eliminados")
                    else:
                        print(f"  ℹ️ {nombre}: Ya estaba vacía")
                except Exception as e2:
                    print(f"  ❌ Error también con SQL directo para {nombre}: {e2}")
                    db.session.rollback()
                    return False
        
        # Mantener solo el usuario administrador
        try:
            usuarios_count = Usuario.query.count()
            admin_user = Usuario.query.filter_by(rol='Administrador').first()
            
            if admin_user:
                # Eliminar todos los usuarios excepto el admin
                Usuario.query.filter(Usuario.id != admin_user.id).delete()
                usuarios_eliminados = usuarios_count - 1
                print(f"  ✅ Usuarios: {usuarios_eliminados} eliminados (mantenido 1 admin)")
            else:
                print("  ⚠️ No se encontró usuario administrador, eliminando todos")
                Usuario.query.delete()
                print(f"  ✅ Usuarios: {usuarios_count} eliminados")
        except Exception as e:
            print(f"  ❌ Error gestionando usuarios: {e}")
            db.session.rollback()
            return False
        
        # Reactivar restricciones de clave foránea para SQLite
        db.session.execute(text("PRAGMA foreign_keys = ON"))
        
        # Confirmar cambios
        db.session.commit()
        print("\n✅ Limpieza de base de datos completada exitosamente")
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la limpieza: {e}")
        db.session.rollback()
        return False

def resetear_secuencias():
    """Resetea las secuencias de auto-incremento para SQLite"""
    print("\n🔄 Reseteando secuencias de auto-incremento...")
    
    tablas = [
        'solicitudes_servicio',
        'ordenes_trabajo', 
        'activos',
        'usuarios',
        'proveedores',
        'archivos_adjuntos',
        'planes_mantenimiento',
        'inventario',
        'movimientos_inventario',
        'manuales',
        'categorias',
        'ordenes_recambio',
        'control_generacion'
    ]
    
    try:
        # Para SQLite, resetear la secuencia usando DELETE en sqlite_sequence
        for tabla in tablas:
            try:
                db.session.execute(text(f"DELETE FROM sqlite_sequence WHERE name='{tabla}'"))
                print(f"  ✅ Secuencia reseteada: {tabla}")
            except Exception as e:
                print(f"  ⚠️ No se pudo resetear {tabla}: {e}")
        
        db.session.commit()
        print("✅ Secuencias reseteadas")
        
    except Exception as e:
        print(f"❌ Error reseteando secuencias: {e}")
        db.session.rollback()

def main():
    """Función principal"""
    print("🚀 Iniciando limpieza de base de datos de producción")
    print("=" * 60)
    
    # Crear aplicación Flask
    app = create_app()
    
    with app.app_context():
        # Verificar estado inicial
        registros_iniciales = verificar_estado_db()
        
        if registros_iniciales == 0:
            print("\n✅ La base de datos ya está limpia")
            return
        
        # Confirmar limpieza
        print(f"\n⚠️ Se van a eliminar {registros_iniciales} registros")
        respuesta = input("¿Continuar con la limpieza? (s/N): ").lower().strip()
        
        if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Limpieza cancelada por el usuario")
            return
        
        # Ejecutar limpieza
        if limpiar_base_datos():
            # Limpiar archivos
            limpiar_archivos_uploads()
            
            # Resetear secuencias
            resetear_secuencias()
            
            # Verificar estado final
            print("\n" + "=" * 60)
            print("🔍 Verificando estado final...")
            registros_finales = verificar_estado_db()
            
            print(f"\n🎉 Limpieza completada exitosamente!")
            print(f"📊 Registros eliminados: {registros_iniciales - registros_finales}")
            print(f"📊 Registros restantes: {registros_finales}")
            
        else:
            print("\n❌ La limpieza falló. Revisa los errores anteriores.")

if __name__ == "__main__":
    main()