"""
Script para recrear las tablas de inventario con la estructura correcta
"""

from app.factory import create_app
from app.extensions import db
from app.models.inventario import Inventario, ConteoInventario, PeriodoInventario
import sqlite3


def recrear_tabla_inventario():
    """Recrear la tabla inventario con la estructura correcta"""

    # Crear la aplicación
    app = create_app()

    with app.app_context():
        # Verificar si hay datos en la tabla inventario
        try:
            inventarios_existentes = Inventario.query.all()
            print(f"Encontrados {len(inventarios_existentes)} registros de inventario")

            # Guardar los datos existentes
            datos_inventario = []
            for inv in inventarios_existentes:
                datos_inventario.append(
                    {
                        "codigo": inv.codigo,
                        "descripcion": inv.descripcion,
                        "categoria": inv.categoria,
                        "subcategoria": inv.subcategoria,
                        "ubicacion": inv.ubicacion,
                        "stock_actual": inv.stock_actual,
                        "stock_minimo": inv.stock_minimo,
                        "stock_maximo": inv.stock_maximo,
                        "unidad_medida": inv.unidad_medida,
                        "precio_unitario": inv.precio_unitario,
                        "precio_promedio": inv.precio_promedio,
                        "proveedor_principal": inv.proveedor_principal,
                        "cuenta_contable_compra": inv.cuenta_contable_compra,
                        "grupo_contable": inv.grupo_contable,
                        "critico": inv.critico,
                        "activo": inv.activo,
                        "observaciones": inv.observaciones,
                        "fecha_creacion": inv.fecha_creacion,
                        "fecha_actualizacion": inv.fecha_actualizacion,
                    }
                )

        except Exception as e:
            print(f"Error al leer datos existentes: {e}")
            datos_inventario = []

        # Eliminar la tabla inventario
        try:
            db.session.execute(db.text("DROP TABLE IF EXISTS inventario"))
            db.session.commit()
            print("Tabla inventario eliminada")
        except Exception as e:
            print(f"Error al eliminar tabla: {e}")

        # Recrear todas las tablas
        try:
            db.create_all()
            print("Tablas recreadas correctamente")
        except Exception as e:
            print(f"Error al crear tablas: {e}")
            return

        # Restaurar los datos
        if datos_inventario:
            try:
                for datos in datos_inventario:
                    inventario = Inventario(**datos)
                    db.session.add(inventario)

                db.session.commit()
                print(f"Restaurados {len(datos_inventario)} registros de inventario")

            except Exception as e:
                print(f"Error al restaurar datos: {e}")
                db.session.rollback()


if __name__ == "__main__":
    recrear_tabla_inventario()
    print("Proceso completado")
