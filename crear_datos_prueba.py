"""
Script para crear datos de prueba y generar órdenes
"""
from datetime import datetime, timedelta
from app import create_app
from app.models.activo import Activo
from app.models.plan_mantenimiento import PlanMantenimiento
from app.extensions import db

app = create_app()

with app.app_context():
    print("Creando datos de prueba...")
    
    # Crear activo de prueba
    activo = Activo(
        nombre="Equipo de Prueba",
        codigo="EQ-TEST-001",
        descripcion="Equipo creado para pruebas",
        ubicacion="Planta principal",
        estado="Operativo",
        departamento="Mantenimiento",
        tipo="Maquinaria",
        activo=True
    )
    db.session.add(activo)
    db.session.flush()  # Para obtener el ID
    
    print(f"✅ Activo creado: {activo.nombre} (ID: {activo.id})")
    
    # Crear plan de mantenimiento
    ahora = datetime.now()
    codigo_plan = f"PM-{ahora.year}-{ahora.month:02d}{ahora.day:02d}"
    
    plan = PlanMantenimiento(
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
    
    db.session.add(plan)
    db.session.commit()
    
    print(f"✅ Plan creado: {plan.codigo_plan}")
    
    # Generar órdenes
    print("\nGenerando órdenes...")
    from app.controllers.planes_controller import generar_ordenes_automaticas
    resultado = generar_ordenes_automaticas()
    
    if resultado["success"]:
        print(f"✅ Generación completada: {resultado.get('ordenes_generadas', 0)} órdenes creadas")
        
        # Verificar órdenes creadas
        from app.models.orden_trabajo import OrdenTrabajo
        ordenes = OrdenTrabajo.query.filter(
            OrdenTrabajo.tipo == "Mantenimiento Preventivo",
            OrdenTrabajo.activo_id == activo.id
        ).all()
        
        if ordenes:
            print("\n=== ÓRDENES GENERADAS ===")
            for orden in ordenes:
                print(f"Orden {orden.numero_orden}: {orden.descripcion}")
                print(f"  Estado: {orden.estado}")
                print(f"  Fecha programada: {orden.fecha_programada}")
        else:
            print("\n⚠️ No se encontraron órdenes generadas")
    else:
        print(f"❌ Error: {resultado.get('error', 'Error desconocido')}")