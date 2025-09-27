#!/usr/bin/env python3
"""
Script para migrar la base de datos con las nuevas tablas de inventario
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

from app.factory import create_app
from app.extensions import db
from sqlalchemy import text


def migrate_inventario_tables():
    app = create_app()

    with app.app_context():
        try:
            print("🔄 Iniciando migración de tablas de inventario...")

            # Comandos SQL para crear las nuevas tablas de inventario
            migration_commands = [
                # Tabla principal de inventario (actualizada)
                """
                CREATE TABLE IF NOT EXISTS inventario_nuevo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo VARCHAR(50) NOT NULL UNIQUE,
                    descripcion VARCHAR(200) NOT NULL,
                    categoria VARCHAR(100),
                    subcategoria VARCHAR(100),
                    ubicacion VARCHAR(100),
                    unidad_medida VARCHAR(20) DEFAULT 'UNI',
                    stock_actual DECIMAL(10,2) DEFAULT 0,
                    stock_minimo DECIMAL(10,2) DEFAULT 0,
                    stock_maximo DECIMAL(10,2),
                    precio_unitario DECIMAL(10,2) DEFAULT 0,
                    precio_promedio DECIMAL(10,2) DEFAULT 0,
                    critico BOOLEAN DEFAULT FALSE,
                    activo BOOLEAN DEFAULT TRUE,
                    cuenta_contable_compra VARCHAR(20) DEFAULT '622000000',
                    grupo_contable VARCHAR(10),
                    proveedor_principal VARCHAR(100),
                    observaciones TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                """,
                # Tabla de conteos de inventario
                """
                CREATE TABLE IF NOT EXISTS conteo_inventario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    periodo_id INTEGER,
                    articulo_id INTEGER NOT NULL,
                    stock_sistema DECIMAL(10,2) NOT NULL,
                    stock_fisico DECIMAL(10,2),
                    diferencia DECIMAL(10,2),
                    estado VARCHAR(20) DEFAULT 'pendiente',
                    usuario_conteo VARCHAR(100),
                    fecha_conteo DATETIME,
                    observaciones TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (articulo_id) REFERENCES inventario_nuevo (id)
                );
                """,
                # Tabla de períodos de inventario
                """
                CREATE TABLE IF NOT EXISTS periodo_inventario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(100) NOT NULL,
                    tipo VARCHAR(20) NOT NULL,
                    fecha_inicio DATE NOT NULL,
                    fecha_fin DATE NOT NULL,
                    estado VARCHAR(20) DEFAULT 'activo',
                    descripcion TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                """,
                # Tabla de asientos contables
                """
                CREATE TABLE IF NOT EXISTS asiento_contable (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero VARCHAR(20) NOT NULL UNIQUE,
                    fecha DATE NOT NULL,
                    concepto VARCHAR(200) NOT NULL,
                    total_debe DECIMAL(12,2) DEFAULT 0,
                    total_haber DECIMAL(12,2) DEFAULT 0,
                    estado VARCHAR(20) DEFAULT 'borrador',
                    movimiento_id INTEGER,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (movimiento_id) REFERENCES movimiento_inventario (id)
                );
                """,
                # Tabla de líneas de asiento contable
                """
                CREATE TABLE IF NOT EXISTS linea_asiento_contable (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asiento_id INTEGER NOT NULL,
                    cuenta_contable VARCHAR(20) NOT NULL,
                    concepto VARCHAR(100) NOT NULL,
                    debe DECIMAL(12,2) DEFAULT 0,
                    haber DECIMAL(12,2) DEFAULT 0,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (asiento_id) REFERENCES asiento_contable (id)
                );
                """,
            ]

            # Ejecutar comandos de migración
            for i, command in enumerate(migration_commands, 1):
                try:
                    db.session.execute(text(command))
                    print(f"✅ Tabla {i}/5 creada correctamente")
                except Exception as e:
                    if (
                        "already exists" in str(e).lower()
                        or "duplicate" in str(e).lower()
                    ):
                        print(f"‚ö†  Tabla {i}/5 ya existe")
                    else:
                        print(f"❌ Error en tabla {i}/5: {e}")
                        raise e

            # Migrar datos existentes si la tabla inventario ya existe
            print("\n🔄 Verificando migración de datos existentes...")

            try:
                # Verificar si existe la tabla inventario original
                result = db.session.execute(
                    text(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name='inventario';"
                    )
                )
                if result.fetchone():
                    print("üìã Tabla inventario original encontrada")

                    # Verificar si ya hay datos en la nueva tabla
                    count_result = db.session.execute(
                        text("SELECT COUNT(*) as count FROM inventario_nuevo;")
                    )
                    count_row = count_result.fetchone()
                    count = count_row[0] if count_row else 0

                    if count == 0:
                        print("🔄 Migrando datos de inventario original...")

                        # Migrar datos básicos
                        migrate_query = """
                        INSERT INTO inventario_nuevo (
                            codigo, descripcion, categoria, ubicacion, 
                            stock_actual, stock_minimo, precio_unitario,
                            fecha_creacion
                        )
                        SELECT 
                            codigo, descripcion, categoria, ubicacion,
                            stock_actual, stock_minimo, precio_unitario,
                            fecha_creacion
                        FROM inventario;
                        """

                        db.session.execute(text(migrate_query))
                        print("✅ Datos migrados correctamente")
                    else:
                        print("‚ö†  La tabla inventario_nuevo ya contiene datos")
                else:
                    print("‚Ñπ  No se encontró tabla inventario original")

            except Exception as e:
                print(f"‚ö†  Error en migración de datos: {e}")

            # Crear índices para mejor rendimiento
            print("\n🔄 Creando índices...")

            index_commands = [
                "CREATE INDEX IF NOT EXISTS idx_inventario_codigo ON inventario_nuevo(codigo);",
                "CREATE INDEX IF NOT EXISTS idx_inventario_categoria ON inventario_nuevo(categoria);",
                "CREATE INDEX IF NOT EXISTS idx_conteo_articulo ON conteo_inventario(articulo_id);",
                "CREATE INDEX IF NOT EXISTS idx_conteo_periodo ON conteo_inventario(periodo_id);",
                "CREATE INDEX IF NOT EXISTS idx_asiento_numero ON asiento_contable(numero);",
                "CREATE INDEX IF NOT EXISTS idx_asiento_fecha ON asiento_contable(fecha);",
                "CREATE INDEX IF NOT EXISTS idx_linea_asiento ON linea_asiento_contable(asiento_id);",
            ]

            for idx_command in index_commands:
                try:
                    db.session.execute(text(idx_command))
                except Exception as e:
                    print(f"‚ö†  √çndice ya existe o error: {e}")

            print("✅ √çndices creados")

            # Confirmar cambios
            db.session.commit()
            print("\nüéâ ¬°Migración de inventario completada exitosamente!")

            # Mostrar resumen
            print("\nüìä Resumen de tablas creadas:")
            print("   - inventario_nuevo: Gestión principal de artículos")
            print("   - conteo_inventario: Conteos físicos")
            print("   - periodo_inventario: Períodos de conteo")
            print("   - asiento_contable: Asientos contables")
            print("   - linea_asiento_contable: Líneas de asientos")

            print("\n🔧 Próximos pasos:")
            print("   1. Ejecutar: python run.py")
            print("   2. Navegar a: http://localhost:5000/inventario")
            print("   3. Probar funcionalidades del módulo")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error durante la migración: {e}")
            raise e


if __name__ == "__main__":
    migrate_inventario_tables()
