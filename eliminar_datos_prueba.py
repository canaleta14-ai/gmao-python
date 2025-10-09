from app import create_app
from app.extensions import db
from sqlalchemy import text

def eliminar_datos_prueba():
    app = create_app()
    print("Eliminando datos de prueba...")
    
    with app.app_context():
        try:
            # Usar transacción independiente para cada tabla
            tablas = [
                'orden_recambio',
                'orden_trabajo',
                'solicitud_servicio',
                'movimiento_inventario',
                'inventario',
                'plan_mantenimiento',
                'activo',
                'control_generacion'
            ]
            
            for tabla in tablas:
                try:
                    # Usar transacción independiente para cada tabla
                    with db.engine.begin() as conn:
                        conn.execute(text(f"TRUNCATE TABLE {tabla} CASCADE"))
                    print(f"  ✅ Tabla {tabla} limpiada")
                except Exception as e:
                    print(f"  ❌ Error al limpiar {tabla}: {str(e)}")
                    
            print("Proceso completado.")
        except Exception as e:
            print(f"Error general: {str(e)}")

if __name__ == "__main__":
    eliminar_datos_prueba()