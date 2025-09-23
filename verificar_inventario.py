"""
Script para verificar que los datos del inventario estén correctos
"""

from app.factory import create_app
from app.models.inventario import Inventario


def verificar_datos():
    """Verificar que los datos del inventario estén correctos"""

    app = create_app()

    with app.app_context():
        try:
            # Contar registros
            total_inventario = Inventario.query.count()
            print(f"Total de artículos en inventario: {total_inventario}")

            # Verificar que la consulta del dashboard funcione
            inventario_bajo = Inventario.query.filter(
                Inventario.stock_actual <= Inventario.stock_minimo
            ).count()
            print(f"Artículos con stock bajo: {inventario_bajo}")

            # Mostrar algunos registros
            articulos = Inventario.query.limit(5).all()
            print("\nPrimeros 5 artículos:")
            for articulo in articulos:
                print(
                    f"  {articulo.codigo} - {articulo.descripcion} (Stock: {articulo.stock_actual})"
                )

            print("\n✅ Verificación completada exitosamente")

        except Exception as e:
            print(f"❌ Error en la verificación: {e}")


if __name__ == "__main__":
    verificar_datos()
