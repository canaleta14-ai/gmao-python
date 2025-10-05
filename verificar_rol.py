"""
Script para verificar el rol del usuario actual y cambiarlo a administrador si es necesario
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.usuario import Usuario


def verificar_y_actualizar_rol():
    """Verifica el rol de los usuarios y permite actualizarlo"""
    app = create_app()

    with app.app_context():
        # Listar todos los usuarios
        usuarios = Usuario.query.all()

        print("\n" + "=" * 60)
        print("📋 USUARIOS EN EL SISTEMA")
        print("=" * 60)

        if not usuarios:
            print("❌ No hay usuarios en el sistema")
            return

        print(f"\n{'ID':<5} {'Usuario':<20} {'Nombre':<25} {'Rol':<15} {'Activo':<8}")
        print("-" * 80)

        for usuario in usuarios:
            activo_str = "✅ Sí" if usuario.activo else "❌ No"
            print(
                f"{usuario.id:<5} {usuario.username:<20} {usuario.nombre:<25} {usuario.rol:<15} {activo_str:<8}"
            )

        print("\n" + "=" * 60)
        print("🔧 ACTUALIZAR ROL A ADMINISTRADOR")
        print("=" * 60)

        # Solicitar el ID del usuario a actualizar
        try:
            user_id = input(
                "\n¿ID del usuario a convertir en administrador? (Enter para cancelar): "
            ).strip()

            if not user_id:
                print("\n❌ Operación cancelada")
                return

            user_id = int(user_id)
            usuario = Usuario.query.get(user_id)

            if not usuario:
                print(f"\n❌ No se encontró usuario con ID {user_id}")
                return

            # Mostrar información del usuario
            print(f"\n📝 Usuario seleccionado:")
            print(f"   Username: {usuario.username}")
            print(f"   Nombre: {usuario.nombre}")
            print(f"   Rol actual: {usuario.rol}")

            confirmar = (
                input(f"\n¿Confirmar cambio a ADMINISTRADOR? (s/N): ").strip().lower()
            )

            if confirmar == "s":
                usuario.rol = "administrador"
                db.session.commit()

                print(f"\n✅ Usuario '{usuario.username}' actualizado a ADMINISTRADOR")
                print(f"\n🔐 Ahora puedes ejecutar la asignación de técnicos")
            else:
                print("\n❌ Operación cancelada")

        except ValueError:
            print("\n❌ ID inválido. Debe ser un número.")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            db.session.rollback()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔐 VERIFICACIÓN Y ACTUALIZACIÓN DE ROLES")
    print("=" * 60)

    verificar_y_actualizar_rol()
