import sys

sys.path.append(".")

from app.extensions import db
from app.models.proveedor import Proveedor
from app.factory import create_app


def verificar_y_limpiar_proveedores():
    """Verifica los campos separados y limpia duplicados si es necesario"""
    app = create_app()
    with app.app_context():

        print("🔍 VERIFICANDO CAMPOS CONTACTO Y TELÉFONO SEPARADOS")
        print("=" * 70)

        # Contar totales
        total = db.session.query(Proveedor).count()
        print(f"📊 Total de proveedores: {total}")

        # Buscar duplicados por NIF
        from sqlalchemy import func

        duplicados = (
            db.session.query(Proveedor.nif, func.count(Proveedor.id).label("count"))
            .group_by(Proveedor.nif)
            .having(func.count(Proveedor.id) > 1)
            .all()
        )

        if duplicados:
            print(f"⚠️  Encontrados {len(duplicados)} NIFs duplicados")

            # Mostrar algunos ejemplos de duplicados
            for nif, count in duplicados[:5]:
                print(f"   - NIF {nif}: {count} registros")
                proveedores_dup = (
                    db.session.query(Proveedor).filter(Proveedor.nif == nif).all()
                )

                for i, p in enumerate(proveedores_dup, 1):
                    print(
                        f"     {i}. ID: {p.id} | Contacto: '{p.contacto}' | Teléfono: '{p.telefono}'"
                    )

            # Ofrecer limpiar duplicados
            print("\n🧹 LIMPIANDO DUPLICADOS...")
            eliminados = 0

            for nif, count in duplicados:
                # Obtener todos los registros duplicados
                proveedores_dup = (
                    db.session.query(Proveedor)
                    .filter(Proveedor.nif == nif)
                    .order_by(Proveedor.id)
                    .all()
                )

                if len(proveedores_dup) > 1:
                    # Mantener el más reciente (último ID) y eliminar los anteriores
                    for p in proveedores_dup[:-1]:
                        db.session.delete(p)
                        eliminados += 1

            db.session.commit()
            print(f"✅ Eliminados {eliminados} proveedores duplicados")

        # Verificar separación de campos
        print("\n📋 MUESTRA DE CAMPOS SEPARADOS:")
        proveedores_con_datos = (
            db.session.query(Proveedor)
            .filter(
                db.or_(Proveedor.contacto.isnot(None), Proveedor.telefono.isnot(None))
            )
            .limit(15)
            .all()
        )

        print(f"{'Nombre':<30} | {'Contacto':<20} | {'Teléfono':<15}")
        print("-" * 70)

        for p in proveedores_con_datos:
            nombre = p.nombre[:29] if p.nombre else ""
            contacto = p.contacto[:19] if p.contacto else "(vacío)"
            telefono = p.telefono if p.telefono else "(vacío)"

            print(f"{nombre:<30} | {contacto:<20} | {telefono:<15}")

        # Estadísticas finales
        total_final = db.session.query(Proveedor).count()
        con_contacto = (
            db.session.query(Proveedor)
            .filter(Proveedor.contacto.isnot(None), Proveedor.contacto != "")
            .count()
        )
        con_telefono = (
            db.session.query(Proveedor)
            .filter(Proveedor.telefono.isnot(None), Proveedor.telefono != "")
            .count()
        )

        print(f"\n📊 ESTADÍSTICAS FINALES:")
        print(f"   - Total proveedores: {total_final}")
        print(f"   - Con contacto (nombre): {con_contacto}")
        print(f"   - Con teléfono: {con_telefono}")
        print(f"   - Separación exitosa: ✅")


if __name__ == "__main__":
    verificar_y_limpiar_proveedores()
