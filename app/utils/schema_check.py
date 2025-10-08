from typing import Dict
from flask import current_app
from sqlalchemy import text
from app.extensions import db


def _get_existing_columns(table: str, schema: str | None) -> set[str]:
    inspector = db.inspect(db.engine)
    return {c["name"] for c in inspector.get_columns(table, schema=schema)}


def ensure_inventario_schema(app=None) -> Dict[str, int]:
    """
    Verifica y corrige columnas faltantes de la tabla inventario en desarrollo/testing.

    - En PostgreSQL usa ALTER TABLE ... ADD COLUMN IF NOT EXISTS en AUTOCOMMIT.
    - En SQLite inspecciona PRAGMA table_info y agrega columnas faltantes.

    Retorna un dict con el número de columnas agregadas por dialecto.
    """
    app = app or current_app
    if not app:
        return {"added": 0}

    # Solo aplicar en desarrollo/testing
    if not (
        app.config.get("TESTING")
        or app.config.get("FLASK_ENV") in ("development", "testing")
        or app.config.get("ENV") == "development"
    ):
        return {"added": 0}

    backend = db.engine.url.get_backend_name() if getattr(db, "engine", None) else None
    schema = "public" if backend in ("postgresql", "postgres") else None

    # Mapa de columnas requeridas y tipos por dialecto
    types_pg = {
        "codigo": "VARCHAR(50)",
        "descripcion": "VARCHAR(200)",
        "nombre": "VARCHAR(100)",
        "cantidad": "INTEGER",
        "cantidad_minima": "INTEGER",
        "unidad": "VARCHAR(20)",
        "categoria_id": "INTEGER",
        "categoria": "VARCHAR(100)",
        "subcategoria": "VARCHAR(100)",
        "ubicacion": "VARCHAR(100)",
        "stock_actual": "NUMERIC(10,2)",
        "stock_minimo": "NUMERIC(10,2)",
        "stock_maximo": "NUMERIC(10,2)",
        "unidad_medida": "VARCHAR(20)",
        "precio_unitario": "NUMERIC(10,2)",
        "precio_promedio": "NUMERIC(10,2)",
        "precio": "NUMERIC(10,2)",
        "proveedor_principal": "VARCHAR(100)",
        "cuenta_contable_compra": "VARCHAR(20)",
        "grupo_contable": "VARCHAR(10)",
        "critico": "BOOLEAN",
        "activo": "BOOLEAN",
        "observaciones": "TEXT",
        "fecha_creacion": "TIMESTAMP",
        "fecha_actualizacion": "TIMESTAMP",
    }

    # SQLite acepta tipos genéricos
    types_sqlite = {k: v.replace("VARCHAR", "TEXT").replace("NUMERIC", "NUMERIC") for k, v in types_pg.items()}

    added = 0
    table_name = "inventario" if not schema else f"{schema}.inventario"

    try:
        existing = _get_existing_columns("inventario", schema)
    except Exception:
        existing = set()

    # Construir lista de columnas faltantes
    missing = [c for c in types_pg.keys() if c not in existing]
    if not missing:
        return {"added": 0}

    with db.engine.connect() as base_conn:
        # Asegurar rollback inicial por si hay transacción abortada
        try:
            base_conn.exec_driver_sql("ROLLBACK")
        except Exception:
            pass

        if backend in ("postgresql", "postgres"):
            # Ejecutar en AUTOCOMMIT para ALTER TABLE
            with base_conn.execution_options(isolation_level="AUTOCOMMIT") as conn:
                for col in missing:
                    coltype = types_pg[col]
                    sql = f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {col} {coltype};"
                    try:
                        conn.exec_driver_sql(sql)
                        added += 1
                    except Exception as e:
                        # Registrar y continuar sin bloquear arranque
                        try:
                            app.logger.warning(f"Error agregando columna {col}: {e}")
                        except Exception:
                            pass
        else:
            # SQLite: no soporta IF NOT EXISTS; verificar y agregar
            for col in missing:
                coltype = types_sqlite[col]
                sql = f"ALTER TABLE inventario ADD COLUMN {col} {coltype};"
                try:
                    base_conn.exec_driver_sql(sql)
                    added += 1
                except Exception as e:
                    try:
                        app.logger.warning(f"Error agregando columna {col} (SQLite): {e}")
                    except Exception:
                        pass

    return {"added": added}