"""
Script para agregar la tabla orden_recambio a la base de datos existente
"""

import sqlite3
import os


def migrar_base_datos():
    # Ruta a la base de datos
    db_path = os.path.join("instance", "database.db")

    if not os.path.exists(db_path):
        print("Base de datos no encontrada. Ejecuta primero init_db.py")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Verificar si la tabla ya existe
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='orden_recambio'"
        )
        if cursor.fetchone():
            print("La tabla orden_recambio ya existe")
            return

        # Crear tabla orden_recambio
        cursor.execute(
            """
            CREATE TABLE orden_recambio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orden_trabajo_id INTEGER NOT NULL,
                inventario_id INTEGER NOT NULL,
                cantidad_solicitada INTEGER NOT NULL,
                cantidad_utilizada INTEGER DEFAULT 0,
                precio_unitario REAL,
                observaciones TEXT,
                fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_descuento DATETIME,
                descontado BOOLEAN DEFAULT 0,
                FOREIGN KEY (orden_trabajo_id) REFERENCES orden_trabajo (id),
                FOREIGN KEY (inventario_id) REFERENCES inventario (id)
            )
        """
        )

        # Crear índices para mejorar performance
        cursor.execute(
            "CREATE INDEX idx_orden_recambio_orden ON orden_recambio(orden_trabajo_id)"
        )
        cursor.execute(
            "CREATE INDEX idx_orden_recambio_inventario ON orden_recambio(inventario_id)"
        )
        cursor.execute(
            "CREATE INDEX idx_orden_recambio_descontado ON orden_recambio(descontado)"
        )

        conn.commit()
        print("✅ Tabla orden_recambio creada exitosamente")
        print("✅ Índices creados exitosamente")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error al crear la tabla: {e}")

    finally:
        conn.close()


if __name__ == "__main__":
    migrar_base_datos()
