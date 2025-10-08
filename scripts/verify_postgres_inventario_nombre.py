import os
from sqlalchemy import create_engine, text


def verify_column(uri: str):
    engine = create_engine(uri)
    with engine.connect() as conn:
        # Intentar con esquema 'public' y sin esquema
        query = text(
            """
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_name = 'inventario'
              AND (table_schema = 'public' OR table_schema NOT IN ('pg_catalog','information_schema'))
              AND column_name = 'nombre'
            """
        )
        count = conn.execute(query).scalar() or 0
        cols = conn.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'inventario'
                  AND (table_schema = 'public' OR table_schema NOT IN ('pg_catalog','information_schema'))
                ORDER BY column_name
                """
            )
        ).fetchall()
        print("inventario columns:", ", ".join([c[0] for c in cols]))
        print("nombre exists:", bool(count))


if __name__ == "__main__":
    uri = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql://postgres@localhost:5432/gmao_db")
    verify_column(uri)