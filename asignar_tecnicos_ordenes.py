"""Script para asignar técnicos a las órdenes de trabajo que no tienen asignación"""

from app.models.orden_trabajo import OrdenTrabajo
from app.models.usuario import Usuario
from app.extensions import db
from app import create_app

# Crear contexto de aplicación
app = create_app()
app.app_context().push()

# Buscar un técnico
tecnico = Usuario.query.filter_by(rol="Técnico").first()

if not tecnico:
    print("❌ No se encontró ningún técnico en la base de datos")
    exit(1)

print(f"✅ Técnico encontrado: {tecnico.nombre} (ID: {tecnico.id})")

# Buscar órdenes sin técnico asignado
ordenes_sin_tecnico = OrdenTrabajo.query.filter_by(tecnico_id=None).all()

print(f"📋 Encontradas {len(ordenes_sin_tecnico)} órdenes sin técnico asignado")

if len(ordenes_sin_tecnico) == 0:
    print("✅ Todas las órdenes ya tienen técnico asignado")
    exit(0)

# Asignar el técnico a todas las órdenes
for orden in ordenes_sin_tecnico:
    orden.tecnico_id = tecnico.id
    print(f"  - Orden #{orden.id} ({orden.numero_orden}): Asignado a {tecnico.nombre}")

# Guardar cambios
db.session.commit()

print(f"\n✅ {len(ordenes_sin_tecnico)} órdenes actualizadas exitosamente")

# Verificar los cambios
ordenes_actualizadas = OrdenTrabajo.query.filter_by(tecnico_id=tecnico.id).all()
print(
    f"🔍 Verificación: {len(ordenes_actualizadas)} órdenes ahora asignadas a {tecnico.nombre}"
)
