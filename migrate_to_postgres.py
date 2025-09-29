#!/usr/bin/env python3
"""
Script para migrar datos de SQLite a PostgreSQL
"""
import os
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, String, TIMESTAMP
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base


def migrate_sqlite_to_postgres(sqlite_path, postgres_uri):
    """
    Migra todos los datos de SQLite a PostgreSQL
    """
    print("🚀 Iniciando migración de SQLite a PostgreSQL...")

    # Conectar a SQLite
    sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
    sqlite_metadata = MetaData()
    sqlite_metadata.reflect(sqlite_engine)

    # Conectar a PostgreSQL con configuración UTF-8
    postgres_uri_with_encoding = postgres_uri + "?client_encoding=utf8"
    postgres_engine = create_engine(
        postgres_uri_with_encoding,
        connect_args={"client_encoding": "utf8", "options": "-c client_encoding=utf8"},
    )
    postgres_metadata = MetaData()
    postgres_metadata.reflect(postgres_engine)

    # Función para convertir tipos de datos de SQLite a PostgreSQL
    def convert_sqlite_to_postgres_type(sqlite_type):
        """Convierte tipos de datos de SQLite a PostgreSQL"""
        type_str = str(sqlite_type).upper()

        # Conversiones principales
        if "DATETIME" in type_str:
            return "TIMESTAMP"
        elif "BOOLEAN" in type_str:
            return "BOOLEAN"
        elif "INTEGER" in type_str:
            return "INTEGER"
        elif "REAL" in type_str:
            return "DOUBLE PRECISION"
        elif "TEXT" in type_str:
            return "TEXT"
        elif "VARCHAR" in type_str:
            return type_str  # Mantener VARCHAR con longitud
        elif "BLOB" in type_str:
            return "BYTEA"
        else:
            # Para otros tipos, intentar mantenerlos
            return str(sqlite_type)

    # Crear tablas en PostgreSQL con tipos de datos convertidos
    for table_name in sqlite_metadata.tables:
        sqlite_table = Table(table_name, sqlite_metadata, autoload_with=sqlite_engine)

        # Crear nueva tabla con tipos convertidos
        columns = []
        for column in sqlite_table.columns:
            # Convertir el tipo de dato
            new_type = convert_sqlite_to_postgres_type(column.type)

            # Crear nueva columna con el tipo convertido
            if "VARCHAR" in str(column.type).upper():
                # Mantener la longitud para VARCHAR
                columns.append(
                    Column(
                        column.name,
                        String(length=column.type.length),
                        primary_key=column.primary_key,
                        nullable=column.nullable,
                        default=column.default,
                        unique=column.unique,
                    )
                )
            elif "DATETIME" in str(column.type).upper():
                columns.append(
                    Column(
                        column.name,
                        TIMESTAMP,
                        primary_key=column.primary_key,
                        nullable=column.nullable,
                        default=column.default,
                        unique=column.unique,
                    )
                )
            else:
                # Para otros tipos, intentar crear la columna con el tipo convertido
                columns.append(
                    Column(
                        column.name,
                        column.type,
                        primary_key=column.primary_key,
                        nullable=column.nullable,
                        default=column.default,
                        unique=column.unique,
                    )
                )

        # Crear tabla en PostgreSQL
        postgres_table = Table(table_name, postgres_metadata, *columns)
        postgres_table.create(postgres_engine, checkfirst=True)

    # Migrar datos tabla por tabla
    for table_name in sqlite_metadata.tables:
        print(f"📋 Migrando tabla: {table_name}")

        sqlite_table = Table(table_name, sqlite_metadata, autoload_with=sqlite_engine)
        postgres_table = Table(
            table_name, postgres_metadata, autoload_with=postgres_engine
        )

        # Obtener todos los datos de SQLite
        with sqlite_engine.connect() as sqlite_conn:
            result = sqlite_conn.execute(sqlite_table.select())
            rows = result.fetchall()

        if rows:
            # Insertar datos en PostgreSQL con manejo de errores y codificación
            with postgres_engine.connect() as postgres_conn:
                try:
                    # Convertir Row objects a dicts con manejo de codificación UTF-8
                    data = []
                    for row in rows:
                        row_dict = {}
                        for key, value in row._mapping.items():
                            # Asegurar que los strings estén en UTF-8 válido
                            if isinstance(value, str):
                                try:
                                    # Verificar que sea UTF-8 válido
                                    value.encode("utf-8")
                                except UnicodeEncodeError:
                                    # Si hay problemas, usar un reemplazo seguro
                                    value = value.encode(
                                        "utf-8", errors="replace"
                                    ).decode("utf-8")
                            row_dict[key] = value
                        data.append(row_dict)

                    postgres_conn.execute(postgres_table.insert(), data)
                    postgres_conn.commit()
                    print(f"✅ Migrados {len(rows)} registros de {table_name}")

                except Exception as e:
                    print(f"❌ Error migrando {table_name}: {e}")
                    postgres_conn.rollback()
                    raise
        else:
            print(f"ℹ️  Tabla {table_name} está vacía")

    print("🎉 Migración completada exitosamente!")


def setup_postgres_database(postgres_uri):
    """
    Crea la base de datos PostgreSQL si no existe
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import OperationalError

    try:
        # Extraer información de conexión
        base_uri = postgres_uri.rsplit("/", 1)[0]  # Todo menos el nombre de la DB
        db_name = postgres_uri.rsplit("/", 1)[1]  # Solo el nombre de la DB

        # Intentar conectar a la base de datos objetivo directamente
        # Si no existe, SQLAlchemy puede crearla en algunos casos
        try:
            engine = create_engine(postgres_uri)
            with engine.connect() as conn:
                print(f"📦 Base de datos '{db_name}' ya existe y es accesible")
            engine.dispose()
            return
        except OperationalError:
            # La base de datos no existe, intentar crearla
            pass

        # Conectar a la base de datos 'postgres' por defecto
        default_db_uri = f"{base_uri}/postgres"
        engine = create_engine(default_db_uri)

        with engine.connect() as conn:
            # Verificar si la base de datos existe
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": db_name},
            )
            if not result.fetchone():
                # Crear la base de datos
                conn.execute(text("COMMIT"))  # Necesario para CREATE DATABASE
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"📦 Base de datos '{db_name}' creada")
            else:
                print(f"📦 Base de datos '{db_name}' ya existe")

        engine.dispose()

    except OperationalError as e:
        if (
            "authentication failed" in str(e).lower()
            or "no password supplied" in str(e).lower()
        ):
            print("⚠️  PostgreSQL requiere configuración de autenticación.")
            print("   Para desarrollo local, ejecuta como administrador:")
            print("   1. net stop postgresql-x64-16")
            print("   2. Edita C:\\Program Files\\PostgreSQL\\16\\data\\pg_hba.conf")
            print("   3. Agrega estas líneas al final:")
            print(
                "      local   all             all                                     trust"
            )
            print(
                "      host    all             all             127.0.0.1/32            trust"
            )
            print("   4. net start postgresql-x64-16")
            print("   O establece las variables de entorno DB_USER y DB_PASSWORD.")
            raise
        else:
            raise


def main():
    # Configuración simplificada para desarrollo local
    sqlite_path = os.path.join(os.path.dirname(__file__), "instance", "database.db")

    # Configuración PostgreSQL para desarrollo local (sin contraseña)
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "gmao_db")
    db_user = os.getenv("DB_USER", "postgres")  # Usuario por defecto
    db_password = os.getenv("DB_PASSWORD", "")  # Sin contraseña para desarrollo

    postgres_uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    # Verificar que el archivo SQLite existe
    if not os.path.exists(sqlite_path):
        print(f"❌ Error: Archivo SQLite no encontrado: {sqlite_path}")
        sys.exit(1)

    try:
        # Crear base de datos PostgreSQL si no existe
        print("🔧 Configurando base de datos PostgreSQL...")
        setup_postgres_database(postgres_uri)

        # Realizar la migración
        migrate_sqlite_to_postgres(sqlite_path, postgres_uri)

        print("\n✅ Migración completada!")
        print(
            f"📝 Para usar PostgreSQL en producción, establece la variable de entorno:"
        )
        print(f"   DB_TYPE=postgresql")
        print(f"   DB_HOST={db_host}")
        print(f"   DB_PORT={db_port}")
        print(f"   DB_NAME={db_name}")
        print(f"   DB_USER={db_user}")
        if db_password:
            print(f"   DB_PASSWORD={db_password}")

    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        print("\n🔧 Solución sugerida:")
        print("1. Asegúrate de que PostgreSQL esté ejecutándose")
        print(
            "2. Para desarrollo local, configura PostgreSQL para permitir conexiones sin contraseña"
        )
        print("3. O establece las variables de entorno DB_USER y DB_PASSWORD")
        sys.exit(1)


if __name__ == "__main__":
    main()
