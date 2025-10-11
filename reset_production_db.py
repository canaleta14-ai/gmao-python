#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import time

def run_command(command, description):
    """Ejecutar un comando y mostrar el resultado"""
    print(f"\n🔄 {description}...")
    print(f"   Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print(f"   ✅ Éxito")
            if result.stdout.strip():
                print(f"   📄 Salida: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Error (código {result.returncode})")
            if result.stderr.strip():
                print(f"   🚨 Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        return False

def reset_production_database():
    """Resetear completamente la base de datos de producción"""
    
    print("=== RESET COMPLETO DE BASE DE DATOS DE PRODUCCIÓN ===\n")
    
    instance_name = "gmao-postgres"
    project_id = "mantenimiento-470311"
    db_name = "gmao"
    
    print(f"🎯 Objetivo: Resetear base de datos '{db_name}' en instancia '{instance_name}'")
    
    # Paso 1: Verificar instancia
    if not run_command(
        f"gcloud sql instances describe {instance_name} --project={project_id}",
        "Verificando instancia de Cloud SQL"
    ):
        print("❌ No se puede acceder a la instancia")
        return False
    
    # Paso 2: Listar bases de datos actuales
    if not run_command(
        f"gcloud sql databases list --instance={instance_name} --project={project_id}",
        "Listando bases de datos actuales"
    ):
        print("❌ No se pueden listar las bases de datos")
        return False
    
    # Paso 3: Intentar eliminar la base de datos
    print(f"\n🗑️ Intentando eliminar base de datos '{db_name}'...")
    delete_success = run_command(
        f"gcloud sql databases delete {db_name} --instance={instance_name} --project={project_id} --quiet",
        f"Eliminando base de datos '{db_name}'"
    )
    
    if delete_success:
        print("   ✅ Base de datos eliminada exitosamente")
        
        # Esperar un momento
        print("   ⏳ Esperando 5 segundos...")
        time.sleep(5)
        
    else:
        print("   ⚠️ No se pudo eliminar la base de datos (puede que no exista o esté en uso)")
    
    # Paso 4: Crear nueva base de datos
    if not run_command(
        f"gcloud sql databases create {db_name} --instance={instance_name} --project={project_id}",
        f"Creando nueva base de datos '{db_name}'"
    ):
        print("❌ No se pudo crear la nueva base de datos")
        return False
    
    print("   ✅ Nueva base de datos creada exitosamente")
    
    # Paso 5: Verificar que la base de datos está limpia
    if not run_command(
        f"gcloud sql databases list --instance={instance_name} --project={project_id}",
        "Verificando bases de datos finales"
    ):
        print("❌ No se pueden verificar las bases de datos")
        return False
    
    print(f"\n✅ RESET DE BASE DE DATOS COMPLETADO")
    print(f"   📊 Base de datos '{db_name}' recreada y completamente limpia")
    print(f"   🏗️ Ahora necesita inicializar las tablas y crear el usuario admin")
    
    return True

def initialize_clean_database():
    """Inicializar la base de datos limpia con estructura y usuario admin"""
    
    print("\n=== INICIALIZACIÓN DE BASE DE DATOS LIMPIA ===\n")
    
    # Crear script de inicialización temporal
    init_script = """
import os
import sys

# Configurar variables de entorno para producción
os.environ['SECRET_KEY'] = 'temp-init-key-2025'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'mantenimiento-470311'
os.environ['FLASK_ENV'] = 'production'
os.environ['DB_TYPE'] = 'postgresql'
os.environ['DB_USER'] = 'gmao-user'
os.environ['DB_NAME'] = 'gmao'
os.environ['DB_HOST'] = '/cloudsql/mantenimiento-470311:europe-west1:gmao-postgres'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.factory import create_app
    from app.extensions import db
    from app.models.usuario import Usuario
    from werkzeug.security import generate_password_hash
    
    app = create_app()
    
    with app.app_context():
        print("🏗️ Creando estructura de tablas...")
        db.create_all()
        
        print("👤 Creando usuario administrador...")
        admin_user = Usuario(
            username='admin',
            email='admin@gmao.com',
            password=generate_password_hash('admin123'),
            nombre='Administrador Sistema',
            rol='Administrador',
            activo=True
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("✅ Inicialización completada exitosamente")
        print(f"👥 Total usuarios: {Usuario.query.count()}")
        
except Exception as e:
    print(f"❌ Error en inicialización: {e}")
    import traceback
    traceback.print_exc()
"""
    
    # Escribir script temporal
    with open("temp_init_clean_db.py", "w", encoding="utf-8") as f:
        f.write(init_script)
    
    # Ejecutar inicialización
    success = run_command(
        "python temp_init_clean_db.py",
        "Inicializando estructura y usuario admin"
    )
    
    # Limpiar archivo temporal
    try:
        import os
        os.remove("temp_init_clean_db.py")
    except:
        pass
    
    return success

if __name__ == "__main__":
    try:
        print("🚨 ADVERTENCIA: Este script eliminará y recreará la base de datos de producción")
        print("🔄 Presiona Ctrl+C para cancelar o Enter para continuar...")
        input()
        
        # Paso 1: Reset de la base de datos
        if reset_production_database():
            print("\n" + "="*60)
            
            # Paso 2: Inicializar base de datos limpia
            if initialize_clean_database():
                print("\n🎉 RESET E INICIALIZACIÓN COMPLETADOS EXITOSAMENTE")
                print("\n🌐 Aplicación de producción:")
                print("   URL: https://mantenimiento-470311.ew.r.appspot.com")
                print("   Login: https://mantenimiento-470311.ew.r.appspot.com/login")
                print("\n🔐 Credenciales únicas de administrador:")
                print("   Usuario: admin")
                print("   Contraseña: admin123")
                print("\n🚨 IMPORTANTE: Cambiar la contraseña inmediatamente")
            else:
                print("\n❌ Error en la inicialización de la base de datos")
        else:
            print("\n❌ Error en el reset de la base de datos")
            
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario.")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()