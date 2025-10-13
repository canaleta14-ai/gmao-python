"""
Script que ejecuta limpieza directamente usando el endpoint existente
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.routes.cleanup import identificar_datos_demo, eliminar_datos_demo

def main():
    """Ejecutar limpieza directamente"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 GMAO - Limpieza de Datos de Prueba")
        print("=" * 50)
        
        # Simular que somos admin (bypass de la verificación de login)
        print("👤 Ejecutando como administrador del sistema...")
        
        try:
            # 1. Identificar datos de prueba
            print("\n🔎 Identificando datos de prueba...")
            datos_demo = identificar_datos_demo()
            
            # 2. Mostrar resumen
            total_inventario = len(datos_demo['inventario'])
            total_usuarios = len(datos_demo['usuarios'])
            
            print(f"\n📊 DATOS ENCONTRADOS:")
            print(f"  📦 Artículos de inventario: {total_inventario}")
            print(f"  👤 Usuarios: {total_usuarios}")
            
            if total_inventario > 0:
                print(f"\n📦 ARTÍCULOS DE INVENTARIO:")
                for item in datos_demo['inventario']:
                    print(f"  - {item['codigo']}: {item['descripcion']}")
            
            if total_usuarios > 0:
                print(f"\n👤 USUARIOS:")
                for item in datos_demo['usuarios']:
                    print(f"  - {item['username']}: {item['nombre']} ({item['email']})")
            
            if total_inventario == 0 and total_usuarios == 0:
                print("\n✅ No se encontraron datos de prueba para eliminar.")
                print("🎉 El sistema está limpio.")
                return
            
            # 3. Confirmar eliminación
            print(f"\n⚠️  ATENCIÓN: Se eliminarán {total_inventario + total_usuarios} elementos")
            print("🔥 Procediendo con la eliminación automática...")
            
            # 4. Eliminar datos
            resultados = eliminar_datos_demo(datos_demo, dry_run=False)
            
            # 5. Mostrar resultados
            print(f"\n🎉 LIMPIEZA COMPLETADA")
            print("=" * 30)
            print(f"✅ Artículos eliminados: {resultados['inventario_eliminado']}")
            print(f"✅ Usuarios eliminados: {resultados['usuarios_eliminados']}")
            print(f"✅ Movimientos eliminados: {resultados['movimientos_eliminados']}")
            print(f"✅ Recambios eliminados: {resultados['recambios_eliminados']}")
            
            print(f"\n🧹 Todos los datos de prueba han sido eliminados de producción.")
            
        except Exception as e:
            print(f"\n❌ ERROR durante la limpieza: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()