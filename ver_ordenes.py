from app import create_app
from app.models.orden_trabajo import OrdenTrabajo

app = create_app()

with app.app_context():
    ordenes = (
        OrdenTrabajo.query.order_by(OrdenTrabajo.fecha_creacion.desc()).limit(5).all()
    )
    print("Últimas 5 órdenes:")
    for o in ordenes:
        print(
            f"ID: {o.id}, Número: {o.numero_orden}, Estado: {o.estado}, Prioridad: {o.prioridad}"
        )
        print(f"  Creada: {o.fecha_creacion}, Activo: {o.activo_id}")
        print(
            f"  Descripción: {o.descripcion[:60]}..."
            if len(o.descripcion) > 60
            else f"  Descripción: {o.descripcion}"
        )
        print()
