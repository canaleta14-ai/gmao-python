from app.extensions import db
from app.models.solicitud_servicio import SolicitudServicio


def crear_tabla_solicitudes():
    """Crear la tabla de solicitudes de servicio"""
    print("Creando tabla de solicitudes de servicio...")

    try:
        # Crear todas las tablas
        db.create_all()
        print("✅ Tabla 'solicitud_servicio' creada exitosamente")

        # Crear algunos datos de prueba
        crear_datos_prueba()

    except Exception as e:
        print(f"❌ Error creando tabla: {e}")
        db.session.rollback()
        raise


def crear_datos_prueba():
    """Crear algunos datos de prueba para solicitudes"""
    print("Creando datos de prueba para solicitudes...")

    try:
        # Verificar si ya existen datos
        if SolicitudServicio.query.count() > 0:
            print("ℹ️ Ya existen datos en la tabla de solicitudes")
            return

        # Crear solicitudes de prueba
        solicitudes_prueba = [
            {
                "numero_solicitud": "SOL-2025-0001",
                "nombre_solicitante": "Juan Pérez",
                "email_solicitante": "juan.perez@empresa.com",
                "telefono_solicitante": "+1234567890",
                "empresa_solicitante": "Empresa ABC",
                "tipo_servicio": "mantenimiento",
                "prioridad": "normal",
                "titulo": "Mantenimiento preventivo de aire acondicionado",
                "descripcion": "El aire acondicionado de la oficina principal presenta ruidos extraños y no enfría correctamente.",
                "ubicacion": "Oficina Principal - Piso 2",
                "activo_afectado": "AA-001",
                "estado": "pendiente",
            },
            {
                "numero_solicitud": "SOL-2025-0002",
                "nombre_solicitante": "María García",
                "email_solicitante": "maria.garcia@empresa.com",
                "telefono_solicitante": "+0987654321",
                "empresa_solicitante": "Empresa XYZ",
                "tipo_servicio": "reparacion",
                "prioridad": "alta",
                "titulo": "Falla en impresora de red",
                "descripcion": "La impresora láser no responde a trabajos de impresión desde hace 2 días.",
                "ubicacion": "Sala de Reuniones",
                "activo_afectado": "IMP-005",
                "estado": "en_progreso",
            },
            {
                "numero_solicitud": "SOL-2025-0003",
                "nombre_solicitante": "Carlos López",
                "email_solicitante": "carlos.lopez@empresa.com",
                "tipo_servicio": "instalacion",
                "prioridad": "baja",
                "titulo": "Instalación de nuevo punto de red",
                "descripcion": "Se requiere instalar un nuevo punto de red en la oficina del gerente.",
                "ubicacion": "Oficina Gerencia",
                "estado": "completada",
            },
        ]

        for datos in solicitudes_prueba:
            solicitud = SolicitudServicio(**datos)
            db.session.add(solicitud)

        db.session.commit()
        print(f"✅ Creadas {len(solicitudes_prueba)} solicitudes de prueba")

    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        db.session.rollback()
        raise


if __name__ == "__main__":
    from app.factory import create_app

    app = create_app()
    with app.app_context():
        crear_tabla_solicitudes()
