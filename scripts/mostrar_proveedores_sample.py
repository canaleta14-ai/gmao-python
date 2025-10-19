import sys

sys.path.append(".")

from app.extensions import db
from app.models.proveedor import Proveedor
from app.factory import create_app


def mostrar_muestra_proveedores():
    """Muestra una muestra de los proveedores importados"""
    app = create_app()
    with app.app_context():
        # Contar totales
        total = db.session.query(Proveedor).count()
        activos = db.session.query(Proveedor).filter(Proveedor.activo == True).count()

        print(f"📊 RESUMEN DE PROVEEDORES:")
        print(f"   Total: {total}")
        print(f"   Activos: {activos}")
        print(f"   Inactivos: {total - activos}")
        print()

        # Mostrar algunos ejemplos con detalles completos
        print("📋 MUESTRA DE PROVEEDORES IMPORTADOS:")
        proveedores = db.session.query(Proveedor).limit(10).all()

        for i, p in enumerate(proveedores, 1):
            print(f"{i:2d}. Nombre: {p.nombre[:50]}...")
            print(f"     NIF: {p.nif}")
            print(f"     Dirección: {p.direccion[:60]}...")
            print(f"     Teléfono: {p.telefono}")
            print(f"     Email: {p.email}")
            print(f"     Cuenta Contable: {p.cuenta_contable}")
            print(f"     Activo: {'✅' if p.activo else '❌'}")
            print()

        # Verificar mapeo de campos específicos
        print("🔍 VERIFICACIÓN DE MAPEO DE CAMPOS:")
        proveedor_test = (
            db.session.query(Proveedor)
            .filter(Proveedor.nombre.like("%ACFLUID%"))
            .first()
        )

        if proveedor_test:
            print(
                f"✅ Campo 'telefono' mapeado desde 'Contacto': {proveedor_test.telefono}"
            )
            print(f"✅ Campo 'activo' mapeado desde 'Estado': {proveedor_test.activo}")

        # Buscar proveedores con emails
        con_email = (
            db.session.query(Proveedor)
            .filter(Proveedor.email != "", Proveedor.email.isnot(None))
            .count()
        )
        print(f"✅ Proveedores con email: {con_email}")


if __name__ == "__main__":
    mostrar_muestra_proveedores()
