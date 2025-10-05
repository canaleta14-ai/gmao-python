"""
Script para actualizar el rol de un usuario directamente en la base de datos de producción
"""

import sqlite3
import sys


def actualizar_rol_produccion():
    """Actualiza el rol de un usuario en la base de datos"""

    # Conectar a la base de datos de producción
    # En App Engine, la BD está en /tmp/database.db o en Cloud SQL
    db_path = input(
        "Ruta de la base de datos (Enter para 'instance/database.db'): "
    ).strip()

    if not db_path:
        db_path = "instance/database.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Listar usuarios
        print("\n" + "=" * 60)
        print("📋 USUARIOS EN LA BASE DE DATOS")
        print("=" * 60)

        cursor.execute("SELECT id, username, nombre, rol, activo FROM usuario")
        usuarios = cursor.fetchall()

        if not usuarios:
            print("❌ No hay usuarios en la base de datos")
            conn.close()
            return

        print(f"\n{'ID':<5} {'Usuario':<20} {'Nombre':<25} {'Rol':<15} {'Activo':<8}")
        print("-" * 80)

        for usuario in usuarios:
            user_id, username, nombre, rol, activo = usuario
            activo_str = "✅ Sí" if activo else "❌ No"
            print(f"{user_id:<5} {username:<20} {nombre:<25} {rol:<15} {activo_str:<8}")

        print("\n" + "=" * 60)
        print("🔧 ACTUALIZAR ROL A ADMINISTRADOR")
        print("=" * 60)

        # Solicitar ID del usuario
        user_id = input(
            "\n¿ID del usuario a convertir en administrador? (Enter para cancelar): "
        ).strip()

        if not user_id:
            print("\n❌ Operación cancelada")
            conn.close()
            return

        # Verificar que el usuario existe
        cursor.execute(
            "SELECT username, nombre, rol FROM usuario WHERE id = ?", (user_id,)
        )
        usuario = cursor.fetchone()

        if not usuario:
            print(f"\n❌ No se encontró usuario con ID {user_id}")
            conn.close()
            return

        username, nombre, rol_actual = usuario

        print(f"\n📝 Usuario seleccionado:")
        print(f"   Username: {username}")
        print(f"   Nombre: {nombre}")
        print(f"   Rol actual: {rol_actual}")

        confirmar = (
            input(f"\n¿Confirmar cambio a ADMINISTRADOR? (s/N): ").strip().lower()
        )

        if confirmar == "s":
            cursor.execute(
                "UPDATE usuario SET rol = 'administrador' WHERE id = ?", (user_id,)
            )
            conn.commit()

            print(f"\n✅ Usuario '{username}' actualizado a ADMINISTRADOR")
            print(f"\n🔐 Ahora puedes ejecutar la asignación de técnicos")
        else:
            print("\n❌ Operación cancelada")

        conn.close()

    except sqlite3.Error as e:
        print(f"\n❌ Error de base de datos: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔐 ACTUALIZACIÓN DE ROL EN BASE DE DATOS")
    print("=" * 60)
    print("\n⚠️  IMPORTANTE: Este script modifica directamente la base de datos")
    print("    Asegúrate de hacer un backup antes de continuar\n")

    continuar = input("¿Continuar? (s/N): ").strip().lower()

    if continuar == "s":
        actualizar_rol_produccion()
    else:
        print("\n❌ Operación cancelada")
