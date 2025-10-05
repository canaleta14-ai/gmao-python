"""
Script para verificar y activar planes de mantenimiento
"""
from datetime import datetime, timedelta
from app import create_app
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.orden_trabajo import OrdenTrabajo
from app.extensions import db

app = create_app()

with app.app_context():
    # Verificar planes existentes
    planes = PlanMantenimiento.query.all()
    print(f"Total planes: {len(planes)}")
    
    if len(planes) == 0:
        print("No hay planes de mantenimiento en el sistema.")
    else:
        print("\n=== PLANES EXISTENTES ===")
        for p in planes:
            print(f"Plan {p.codigo_plan}: Estado={p.estado}, Próxima ejecución={p.proxima_ejecucion}, Generación automática={p.generacion_automatica}")
            
            # Activar planes y configurar para generación automática
            if p.estado != "Activo" or not p.generacion_automatica:
                p.estado = "Activo"
                p.generacion_automatica = True
                print(f"  → Activando plan {p.codigo_plan}")
            
            # Establecer próxima ejecución para hoy si no está configurada o es futura
            ahora = datetime.now()
            p.proxima_ejecucion = ahora - timedelta(minutes=5)  # 5 minutos en el pasado para que se genere
            print(f"  → Configurando próxima ejecución a {p.proxima_ejecucion}")
            
            # Verificar si ya existe una orden pendiente para este plan
            ordenes_existentes = OrdenTrabajo.query.filter(
                OrdenTrabajo.tipo == "Mantenimiento Preventivo",
                OrdenTrabajo.activo_id == p.activo_id,
                OrdenTrabajo.descripcion.contains(f"Plan: {p.codigo_plan}"),
                OrdenTrabajo.estado.in_(["Pendiente", "En Proceso"]),
            ).all()
            
            if ordenes_existentes:
                print(f"  ⚠️ Ya existen {len(ordenes_existentes)} órdenes pendientes para este plan")
                # Eliminar órdenes existentes para permitir crear nuevas
                for orden in ordenes_existentes:
                    print(f"    → Eliminando orden {orden.numero_orden}")
                    db.session.delete(orden)
        
        # Guardar cambios
        db.session.commit()
        print("\n✅ Planes actualizados correctamente")
        
    print("\nEjecutando generación de órdenes...")
    from app.controllers.planes_controller import generar_ordenes_automaticas
    resultado = generar_ordenes_automaticas()
    
    if resultado["success"]:
        print(f"✅ Generación completada: {resultado.get('ordenes_generadas', 0)} órdenes creadas")
        
        # Mostrar las órdenes generadas
        ordenes = OrdenTrabajo.query.filter(
            OrdenTrabajo.tipo == "Mantenimiento Preventivo",
            OrdenTrabajo.estado == "Pendiente"
        ).all()
        
        if ordenes:
            print("\n=== ÓRDENES GENERADAS ===")
            for orden in ordenes:
                print(f"Orden {orden.numero_orden}: {orden.descripcion}")
                print(f"  Estado: {orden.estado}")
                print(f"  Fecha programada: {orden.fecha_programada}")
                print(f"  Activo ID: {orden.activo_id}")
                print("  ---")
        else:
            print("\n⚠️ No se encontraron órdenes generadas en el sistema")
    else:
        print(f"❌ Error: {resultado.get('error', 'Error desconocido')}")