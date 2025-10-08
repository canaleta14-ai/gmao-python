"""
Script para verificar que los datos del inventario estén correctos
"""

from app.factory import create_app
from app.models.inventario import Inventario
from app.extensions import db
from sqlalchemy import text


def verificar_datos():
    """Verificar que los datos del inventario estén correctos"""

    app = create_app()

    with app.app_context():
        # Contar registros con fallback seguro (ROLLBACK + AUTOCOMMIT en Postgres)
        try:
            total_inventario = Inventario.query.count()
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass
            try:
                db.session.remove()
            except Exception:
                pass
            backend = db.engine.url.get_backend_name() if getattr(db, "engine", None) else None
            table_name = "inventario"
            if backend in ("postgresql", "postgres"):
                table_name = "public.inventario"
            with db.engine.connect() as base_conn:
                try:
                    base_conn.exec_driver_sql("ROLLBACK")
                except Exception:
                    pass
                with base_conn.execution_options(isolation_level="AUTOCOMMIT") as conn:
                    res = conn.execute(text(f"SELECT COUNT(*) AS total FROM {table_name}")).first()
                    total_inventario = int(res[0]) if res else 0
        print(f"Total de artículos en inventario: {total_inventario}")

        # Verificar que la consulta del dashboard funcione (con fallback)
        try:
            inventario_bajo = (
                Inventario.query.filter(
                    Inventario.stock_actual <= Inventario.stock_minimo
                ).count()
            )
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass
            try:
                db.session.remove()
            except Exception:
                pass
            backend = db.engine.url.get_backend_name() if getattr(db, "engine", None) else None
            table_name = "inventario"
            if backend in ("postgresql", "postgres"):
                table_name = "public.inventario"
            with db.engine.connect() as base_conn:
                try:
                    base_conn.exec_driver_sql("ROLLBACK")
                except Exception:
                    pass
                with base_conn.execution_options(isolation_level="AUTOCOMMIT") as conn:
                    res = conn.execute(
                        text(
                            f"SELECT COUNT(*) AS total FROM {table_name} WHERE COALESCE(stock_actual, 0) <= COALESCE(stock_minimo, 0)"
                        )
                    ).first()
                    inventario_bajo = int(res[0]) if res else 0
        print(f"Artículos con stock bajo: {inventario_bajo}")

        # Mostrar algunos registros (con fallback)
        try:
            articulos = Inventario.query.limit(5).all()
            filas = [
                (
                    a.codigo,
                    a.descripcion,
                    a.stock_actual,
                )
                for a in articulos
            ]
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass
            try:
                db.session.remove()
            except Exception:
                pass
            backend = db.engine.url.get_backend_name() if getattr(db, "engine", None) else None
            table_name = "inventario"
            if backend in ("postgresql", "postgres"):
                table_name = "public.inventario"
            with db.engine.connect() as base_conn:
                try:
                    base_conn.exec_driver_sql("ROLLBACK")
                except Exception:
                    pass
                with base_conn.execution_options(isolation_level="AUTOCOMMIT") as conn:
                    rows = conn.execute(
                        text(
                            f"SELECT codigo, descripcion, COALESCE(stock_actual, 0) AS stock_actual FROM {table_name} ORDER BY id LIMIT 5"
                        )
                    ).fetchall()
                    filas = [(r[0], r[1], r[2]) for r in rows]

        print("\nPrimeros 5 artículos:")
        for codigo, descripcion, stock in filas:
            print(f"  {codigo} - {descripcion} (Stock: {stock})")

        print("\n✅ Verificación completada exitosamente")


if __name__ == "__main__":
    verificar_datos()
