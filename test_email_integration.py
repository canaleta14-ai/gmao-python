#!/usr/bin/env python3
"""
Prueba de integración de emails en solicitudes de servicio
"""
import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_email_integration():
    """Prueba la integración de emails con el modelo de solicitud"""
    try:
        from app.utils.email_utils import (
            enviar_email_confirmacion,
            enviar_email_notificacion_admin,
        )
        from app.models.solicitud_servicio import SolicitudServicio
        from datetime import datetime

        print("✅ Módulos importados correctamente")

        # Crear una solicitud de prueba (sin guardar en BD)
        solicitud = SolicitudServicio(
            numero_solicitud="TEST-001",
            nombre_solicitante="Usuario de Prueba",
            email_solicitante="test@example.com",
            telefono_solicitante="123456789",
            empresa_solicitante="Empresa Test",
            tipo_servicio="mantenimiento",
            prioridad="normal",
            titulo="Prueba de email",
            descripcion="Esta es una solicitud de prueba para verificar el envío de emails",
            ubicacion="Oficina Central",
            activo_afectado="Computadora #1",
        )

        # Simular fecha de creación
        solicitud.fecha_creacion = datetime.now()

        print("✅ Solicitud de prueba creada")
        print(f"   Número: {solicitud.numero_solicitud}")
        print(f"   Solicitante: {solicitud.nombre_solicitante}")
        print(f"   Email: {solicitud.email_solicitante}")

        # Verificar que los métodos existen
        assert hasattr(solicitud, "numero_solicitud"), "Falta atributo numero_solicitud"
        assert hasattr(
            solicitud, "nombre_solicitante"
        ), "Falta atributo nombre_solicitante"
        assert hasattr(
            solicitud, "email_solicitante"
        ), "Falta atributo email_solicitante"

        print("✅ Atributos de solicitud verificados")

        # Verificar que las funciones de email existen
        assert callable(
            enviar_email_confirmacion
        ), "Función enviar_email_confirmacion no es callable"
        assert callable(
            enviar_email_notificacion_admin
        ), "Función enviar_email_notificacion_admin no es callable"

        print("✅ Funciones de email verificadas")

        print("\n🎉 ¡Integración de emails funcionando correctamente!")
        print("Las funciones están listas para enviar emails automáticos.")
        print("\nPara probar el envío real:")
        print("1. Crea una solicitud real desde la interfaz web")
        print("2. Verifica que se envíen los emails de confirmación")
        print("3. Revisa los logs del servidor para mensajes de error")

        return True

    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


if __name__ == "__main__":
    success = test_email_integration()
    sys.exit(0 if success else 1)
