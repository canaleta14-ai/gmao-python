import pandas as pd
from app.extensions import db
from app.models.proveedor import Proveedor
from app.factory import create_app

def cargar_proveedores_desde_excel(ruta_excel):
    df = pd.read_excel(ruta_excel)
    for _, row in df.iterrows():
        proveedor = Proveedor(
            nombre=row.get('Proveedor', ''),
            nif=row.get('NIF', ''),
            direccion=row.get('Dirección', ''),
            contacto=row.get('Contacto', ''),
            email=row.get('Email', ''),
            cuenta_contable=row.get('Cuenta Contable', ''),
            estado=row.get('Estado', '')
        )
        db.session.add(proveedor)
    db.session.commit()
    print(f"Cargados {len(df)} proveedores desde {ruta_excel}")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        cargar_proveedores_desde_excel("Proveedores.xlsx")
