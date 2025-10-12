#!/usr/bin/env python3
"""
Script para activar proveedor Sonepar en producción
Ejecutar: python scripts/activar_sonepar.py
"""

from app.factory import create_app
from app.models.proveedor import Proveedor
from app.extensions import db


def activar_sonepar():
    """Activar el proveedor Sonepar en la base de datos"""
    print("🔄 Iniciando activación de proveedor Sonepar...")

    try:
        # Buscar el proveedor Sonepar
        sonepar = Proveedor.query.filter_by(nombre="Sonepar").first()

        if not sonepar:
            print("❌ No se encontró el proveedor 'Sonepar'")
            return False

        print(f"✅ Proveedor encontrado:")
        print(f"   ID: {sonepar.id}")
        print(f"   Nombre: {sonepar.nombre}")
        print(f"   NIF: {sonepar.nif}")
        print(f"   Estado actual: {'ACTIVO' if sonepar.activo else 'INACTIVO'}")

        if sonepar.activo:
            print("✅ El proveedor ya está activo. No es necesario hacer cambios.")
            return True

        # Activar el proveedor
        print("🔄 Activando proveedor...")
        sonepar.activo = True
        db.session.commit()

        print("✅ ¡Proveedor Sonepar activado exitosamente!")
        print("🎯 Ahora debería aparecer en el select de proveedores al crear activos.")

        return True

    except Exception as e:
        print(f"❌ Error al activar proveedor: {e}")
        db.session.rollback()
        return False


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        success = activar_sonepar()
        if success:
            print("\n🎉 ¡Activación completada!")
            print(
                "📋 Puedes verificar con: python -c \"from app.factory import create_app; from app.controllers.proveedores_controller import listar_proveedores; app = create_app(); app.app_context().push(); print([p for p in listar_proveedores() if p.get('activo')])\""
            )
        else:
            print("\n❌ La activación falló. Revisa los logs arriba.")
