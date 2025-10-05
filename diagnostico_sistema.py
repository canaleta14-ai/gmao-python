"""
Script de diagnóstico para verificar activos y planes en el sistema
"""
from app import create_app
from app.models.activo import Activo
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.orden_trabajo import OrdenTrabajo
from app.extensions import db
from datetime import datetime

app = create_app()

with app.app_context():
    print("\n===== DIAGNÓSTICO DEL SISTEMA =====\n")
    
    # Verificar activos
    activos = Activo.query.all()
    print(f"ACTIVOS EN EL SISTEMA: {len(activos)}")
    if activos:
        for i, activo in enumerate(activos[:5], 1):  # Mostrar solo los primeros 5
            print(f"{i}. ID: {activo.id} - {activo.nombre} - {activo.codigo}")
        if len(activos) > 5:
            print(f"   ... y {len(activos) - 5} activos más")
    else:
        print("⚠️ NO HAY ACTIVOS EN EL SISTEMA")
    
    # Verificar planes
    planes = PlanMantenimiento.query.all()
    print(f"\nPLANES DE MANTENIMIENTO: {len(planes)}")
    if planes:
        for i, plan in enumerate(planes, 1):
            print(f"{i}. ID: {plan.id} - Código: {plan.codigo_plan} - {plan.nombre}")
            print(f"   Activo ID: {plan.activo_id}")
            print(f"   Estado: {plan.estado}")
            print(f"   Generación automática: {plan.generacion_automatica}")
            print(f"   Próxima ejecución: {plan.proxima_ejecucion}")
            print(f"   Tipo frecuencia: {plan.tipo_frecuencia}")
            
            # Verificar si el activo existe
            activo = Activo.query.get(plan.activo_id)
            if not activo:
                print(f"   ⚠️ ERROR: El activo con ID {plan.activo_id} no existe")
    else:
        print("⚠️ NO HAY PLANES DE MANTENIMIENTO EN EL SISTEMA")
    
    # Verificar órdenes
    ordenes = OrdenTrabajo.query.filter(
        OrdenTrabajo.tipo == "Mantenimiento Preventivo"
    ).all()
    print(f"\nÓRDENES DE MANTENIMIENTO PREVENTIVO: {len(ordenes)}")
    if ordenes:
        for i, orden in enumerate(ordenes[:5], 1):  # Mostrar solo las primeras 5
            print(f"{i}. {orden.numero_orden} - {orden.descripcion}")
            print(f"   Estado: {orden.estado}")
            print(f"   Fecha programada: {orden.fecha_programada}")
        if len(ordenes) > 5:
            print(f"   ... y {len(ordenes) - 5} órdenes más")
    else:
        print("⚠️ NO HAY ÓRDENES DE MANTENIMIENTO PREVENTIVO")
    
    print("\n===== FIN DEL DIAGNÓSTICO =====")