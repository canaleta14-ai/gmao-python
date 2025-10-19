import sys

sys.path.append(".")

from app.extensions import db
from app.factory import create_app
from sqlalchemy import text


def verificar_estructura_tabla():
    """Verifica la estructura actual de la tabla proveedor"""
    app = create_app()
    with app.app_context():
        # Consultar la estructura de la tabla
        result = db.session.execute(
            text(
                """
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'proveedor' 
            ORDER BY ordinal_position;
        """
            )
        )

        print("📋 ESTRUCTURA ACTUAL DE LA TABLA 'proveedor':")
        print("=" * 60)
        for row in result:
            nullable = "SÍ" if row.is_nullable == "YES" else "NO"
            length = (
                f"({row.character_maximum_length})"
                if row.character_maximum_length
                else ""
            )
            print(
                f"  {row.column_name:<20} | {row.data_type:<15}{length:<8} | Nulo: {nullable}"
            )

        print("\n🔍 VERIFICANDO CAMPOS ESPECÍFICOS:")

        # Verificar si existe la columna contacto
        contacto_exists = db.session.execute(
            text(
                """
            SELECT COUNT(*) as count
            FROM information_schema.columns 
            WHERE table_name = 'proveedor' AND column_name = 'contacto';
        """
            )
        ).scalar()

        telefono_exists = db.session.execute(
            text(
                """
            SELECT COUNT(*) as count
            FROM information_schema.columns 
            WHERE table_name = 'proveedor' AND column_name = 'telefono';
        """
            )
        ).scalar()

        print(
            f"  ✅ Campo 'contacto': {'EXISTE' if contacto_exists > 0 else 'NO EXISTE'}"
        )
        print(
            f"  ✅ Campo 'telefono': {'EXISTE' if telefono_exists > 0 else 'NO EXISTE'}"
        )

        if contacto_exists == 0:
            print("\n⚠️  ATENCIÓN: El campo 'contacto' no existe en la base de datos")
            print("   Necesitas crear una migración para añadir este campo.")

        if telefono_exists == 0:
            print("\n⚠️  ATENCIÓN: El campo 'telefono' no existe en la base de datos")
            print("   Necesitas crear una migración para añadir este campo.")


if __name__ == "__main__":
    verificar_estructura_tabla()
