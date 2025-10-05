"""
Script para crear un plan de mantenimiento de prueba
"""
from datetime import datetime, timedelta
from app import create_app
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.activo import Activo
from app.extensions import db

app = create_app()

with app.app_context():
    # Verificar si hay activos en el sistema
    activos = Activo.query.all()
    
    if not activos:
        print("❌ No hay activos en el sistema. No se puede crear un plan.")
        exit(1)
    
    # Usar el primer activo disponible
    activo = activos[0]
    print(f"Usando activo: {activo.nombre} (ID: {activo.id})")
    
    # Crear plan de mantenimiento
    ahora = datetime.now()
    codigo_plan = f"PM-{ahora.year}-{ahora.month:02d}{ahora.day:02d}"
    
    nuevo_plan = PlanMantenimiento(
        codigo_plan=codigo_plan,
        nombre="Plan de mantenimiento de prueba",
        descripcion="Plan creado automáticamente para pruebas",
        estado="Activo",
        activo_id=activo.id,
        tipo_frecuencia="diaria",
        frecuencia_dias=1,
        proxima_ejecucion=ahora - timedelta(minutes=5),  # 5 minutos en el pasado para que se genere
        generacion_automatica=True,
        tiempo_estimado=60,  # 60 minutos
        instrucciones="1. Revisar equipo\n2. Realizar limpieza\n3. Verificar funcionamiento"
    )
    
    db.session.add(nuevo_plan)
    db.session.commit()
    
    print(f"✅ Plan creado: {codigo_plan}")
    print(f"Próxima ejecución: {nuevo_plan.proxima_ejecucion}")
    
    # Generar órdenes
    print("\nGenerando órdenes...")
    from app.controllers.planes_controller import generar_ordenes_automaticas
    resultado = generar_ordenes_automaticas()
    
    if resultado["success"]:
        print(f"✅ Generación completada: {resultado.get('ordenes_generadas', 0)} órdenes creadas")
    else:
        print(f"❌ Error: {resultado.get('error', 'Error desconocido')}")