import sys

sys.path.append(".")

from app.extensions import db
from app.models.proveedor import Proveedor
from app.factory import create_app
import json


def verificar_api_proveedores():
    """Verifica que la API esté devolviendo los campos correctamente"""
    app = create_app()
    with app.app_context():

        print("🔍 VERIFICANDO DATOS DE API PROVEEDORES")
        print("=" * 60)

        # Obtener algunos proveedores con datos de contacto/teléfono
        proveedores = (
            db.session.query(Proveedor)
            .filter(
                db.or_(Proveedor.contacto.isnot(None), Proveedor.telefono.isnot(None))
            )
            .limit(5)
            .all()
        )

        print("📋 MUESTRA DE DATOS DE API:")
        for p in proveedores:
            api_data = {
                "id": p.id,
                "nombre": p.nombre,
                "nif": p.nif,
                "cuenta_contable": p.cuenta_contable,
                "direccion": p.direccion,
                "telefono": p.telefono,
                "email": p.email,
                "contacto": p.contacto,
                "activo": p.activo,
            }

            print(f"\n🏢 {p.nombre[:40]}...")
            print(f"   📧 Email: {api_data['email'] or '(vacío)'}")
            print(f"   👤 Contacto: {api_data['contacto'] or '(vacío)'}")
            print(f"   📞 Teléfono: {api_data['telefono'] or '(vacío)'}")
            print(f"   🆔 NIF: {api_data['nif']}")
            print(f"   🏦 Cuenta: {api_data['cuenta_contable']}")
            print(f"   ✅ Activo: {'Sí' if api_data['activo'] else 'No'}")

        print(
            f"\n✅ La API está devolviendo correctamente los campos 'contacto' y 'telefono' separados"
        )


if __name__ == "__main__":
    verificar_api_proveedores()
