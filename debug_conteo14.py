#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect("instance/database.db")
cursor = conn.cursor()

# Verificar conteo 14
cursor.execute("SELECT * FROM conteo_inventario WHERE id = 14")
result = cursor.fetchone()
if result:
    print(f"Conteo 14: {result}")

    # También verificar el artículo asociado
    cursor.execute(
        "SELECT id, codigo, descripcion, stock_actual, precio_promedio FROM inventario WHERE id = ?",
        (result[9],),
    )  # inventario_id es la columna 9
    articulo = cursor.fetchone()
    if articulo:
        print(
            f"Artículo: ID={articulo[0]}, Código={articulo[1]}, Desc={articulo[2]}, Stock={articulo[3]}, Precio={articulo[4]}"
        )
    else:
        print("No se encontró el artículo asociado")
else:
    print("No se encontró el conteo 14")

conn.close()
