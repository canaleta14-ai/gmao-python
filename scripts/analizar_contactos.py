import sys

sys.path.append(".")

from app.extensions import db
from app.models.proveedor import Proveedor
from app.factory import create_app
import pandas as pd


def analizar_datos_contacto():
    """Analiza los datos actuales de contacto para entender el formato"""

    print("🔍 ANALIZANDO DATOS DE CONTACTO ACTUALES")
    print("=" * 60)

    # Leer Excel original
    print("📋 DATOS DEL EXCEL ORIGINAL:")
    try:
        df = pd.read_excel("Proveedores.xlsx")
        contacto_excel = df["Contacto"].dropna()

        print(f"  Total de contactos en Excel: {len(contacto_excel)}")
        print("  Primeros 10 valores de 'Contacto' en Excel:")
        for i, valor in enumerate(contacto_excel.head(10), 1):
            print(f"    {i:2d}. {valor}")

        print("\n  Análisis de contenido:")
        # Intentar determinar si son números o nombres
        numeros = 0
        nombres = 0
        mixtos = 0

        for valor in contacto_excel:
            valor_str = str(valor).strip()
            if valor_str.isdigit():
                numeros += 1
            elif any(char.isalpha() for char in valor_str):
                if any(char.isdigit() for char in valor_str):
                    mixtos += 1
                else:
                    nombres += 1

        print(f"    - Solo números: {numeros}")
        print(f"    - Solo texto/nombres: {nombres}")
        print(f"    - Mixto (números + texto): {mixtos}")

    except Exception as e:
        print(f"  ❌ Error leyendo Excel: {e}")

    # Revisar base de datos
    print("\n📊 DATOS EN LA BASE DE DATOS:")
    app = create_app()
    with app.app_context():
        proveedores = (
            db.session.query(Proveedor)
            .filter(Proveedor.telefono.isnot(None), Proveedor.telefono != "")
            .limit(10)
            .all()
        )

        print(f"  Total proveedores con 'telefono' no vacío: {len(proveedores)}")
        print("  Primeros 10 valores de 'telefono' en BD:")
        for i, p in enumerate(proveedores, 1):
            print(f"    {i:2d}. {p.nombre[:30]}... -> telefono: '{p.telefono}'")

        # Verificar campo contacto actual
        contactos_bd = (
            db.session.query(Proveedor)
            .filter(Proveedor.contacto.isnot(None), Proveedor.contacto != "")
            .limit(5)
            .all()
        )

        print(f"\n  Proveedores con 'contacto' no vacío: {len(contactos_bd)}")
        if contactos_bd:
            print("  Valores de 'contacto' en BD:")
            for i, p in enumerate(contactos_bd, 1):
                print(f"    {i:2d}. {p.nombre[:30]}... -> contacto: '{p.contacto}'")
        else:
            print("  ⚠️ No hay proveedores con campo 'contacto' lleno")


if __name__ == "__main__":
    analizar_datos_contacto()
